from typing import List, Optional, Sequence
from langchain.docstore.document import Document
import os
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_core.output_parsers import StrOutputParser
from sentence_transformers import CrossEncoder
from langchain_core.documents.compressor import BaseDocumentCompressor
from langchain_core.callbacks import Callbacks
from pydantic import Field, PrivateAttr
from langchain.schema import Document
from langchain_community.retrievers import BM25Retriever
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import re

class FastKeywordRetriever:
    def __init__(self, docs, top_k=100):
        self.docs = docs
        self.top_k = top_k

    def invoke(self, query: str):
        pattern = re.compile(re.escape(query))  # 编译正则匹配
        hits = [doc for doc in self.docs if pattern.search(doc.page_content)]
        return hits[:self.top_k]

class CrossEncoderReranker(BaseDocumentCompressor):
    #将top_k声明为Pydantic 字段
    top_k: int = Field(1, description="Number of top documents to return")
    #声明一个私有属性来存储CrossEncoder
    _reranker: CrossEncoder = PrivateAttr()

    def __init__(
        self,
        model_name_or_path: str = "cross-encoder/ms-marco-MiniLM-L-12-v2",
        top_k: int = 3,
        use_gpu: bool = True,
        **kwargs
    ):
        """Pydantic 要求在 super().__init__ 中显式传入已声明字段 (如 top_k)。"""
        super().__init__(top_k=top_k, **kwargs)

        device = "cuda" if use_gpu else "cpu"
        #将 CrossEncoder模型存储到私有属性里
        self._reranker = CrossEncoder(model_name_or_path, device=device)

    def rerank(self, query: str, docs: List[Document]) -> List[Document]:
        if not docs:
            return []
        pairs = [(query, d.page_content) for d in docs]
        scores = self._reranker.predict(pairs)
        docs_with_scores = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
        top_docs = [d for d, s in docs_with_scores[: self.top_k]]
        return top_docs

    def compress_documents(
        self, documents: Sequence[Document], query: str, callbacks: Optional[Callbacks] = None
    ) -> Sequence[Document]:
        """Required by BaseDocumentCompressor; delegates to `rerank`."""
        return self.rerank(query, list(documents))

import re

def filter_docs_by_main_ingredients(top_docs, keywords, top_k=1):
    filtered_docs = []
    for doc in top_docs:
        # 提取所有主料名（主料：XXX（...））
        main_ingredients = re.findall(r"主料：([\u4e00-\u9fa5]+)", doc)
        if main_ingredients:
            # 所有主料都必须出现在关键词中
            if all(ingredient in keywords for ingredient in main_ingredients):
                filtered_docs.append(doc)
    
    # 限制返回前 top_k 个（如果 top_k 有设置）
    if top_k is not None:
        return filtered_docs[:top_k]
    return filtered_docs

    
def build_langchain_pipeline(
    documents: List[Document],
    default_prompt_template: str,
    top_k: int = 100,
    keywords: List[str] = ['鸡蛋盒', '生菜', '胡萝卜', '猪肉', '嫩豆腐', '茄子'],
):
    #fewshotpipeline = FewShotPipeline(q_list, a_list, topk)
    # bm25_retriever = BM25Retriever.from_documents(documents,k=100)#input: List[Document],run :query:str->List[Document]
    # reranker1 = CrossEncoderReranker(top_k = top_k)

    # reranker = ContextualCompressionRetriever(
    #     base_compressor=reranker1, base_retriever=bm25_retriever
    # )
    reranker=FastKeywordRetriever(documents)
    llm = ChatOpenAI(
        model_name="gpt-4o",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0,
        max_tokens=4096
    )

    prompt_temp = PromptTemplate(
        template=default_prompt_template,
        input_variables=["context", "question"],
    )
    chain = prompt_temp | llm | StrOutputParser()

    def run(query: str) -> str:
        reranked_docs = reranker.invoke(query)#猪肉 查到100个
        reranked_docs = [d.page_content for d in reranked_docs]
        
        top_docs = reranked_docs[:top_k]#100个猪肉
        ##############################消融实验
        # top_docs = reranked_docs[:0]
        result = filter_docs_by_main_ingredients(top_docs, keywords)#前100个猪肉
        #print('here is top documents', result,'++++++')
        # context = "\n\n".join(doc for doc in top_docs)
        context = "\n\n".join(doc for doc in result)
        print('here is context', context,'++++++',keywords)
        #few_shot_example = fewshotpipeline.run(query)#进入query输出相关question的qa对
        #return chain.invoke({"context": context, "question": query, "few_shot_example": few_shot_example})
        return chain.invoke({"context": context, "question": query})

    return run
def load_txt_files(folder_path):
    docs = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            docs.append(Document(page_content=content, metadata={"source": file_path}))
                except Exception as e:
                    print(f"fail to load {file_path} error: {e}")

    return docs

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

class ParagraphThenCharacterSplitter:
    def __init__(self):
        pass  # 如果不需要再处理 chunk_size 和 chunk_overlap，可去掉或留空

    def split_document(self, doc):
        # 仅按照两个换行符分割文档
        paragraphs = doc.page_content.split("\n\n")
        final_chunks = []

        for paragraph in paragraphs:
            # 去除前后空白
            paragraph = paragraph.strip()
            # 如果当前段落非空，则作为一个 chunk
            if paragraph:
                final_chunks.append(
                    Document(page_content=paragraph, metadata=doc.metadata)
                )

        return final_chunks

    def process(self, docs):
        processed_docs = []
        for doc in docs:
            processed_docs.extend(self.split_document(doc))
        return processed_docs

def save_list_to_txt(sentences, file_path, encoding="utf-8"):
    try:
        with open(file_path, "w", encoding=encoding) as f:
            for sentence in sentences:
                f.write(sentence.strip() + "\n")
        print(f"successfully save the txt: {file_path}")
    except Exception as e:
        print(f"fail to save, error: {e}")

import json
def extract_answer(text):
    text = text.split("Answer:", 1)[-1].strip()
    #return text.split("\n\n", 1)[0].strip()
    return text

def smart_fridge_RAG(knowledge_path='RAG/scrape',keywords = ['鸡蛋盒', '生菜', '胡萝卜', '猪肉', '嫩豆腐', '茄子']):
    folder_path = knowledge_path
    docs = load_txt_files(folder_path)
    docs_processed = ParagraphThenCharacterSplitter().process(docs)
    sample_docs = docs_processed
    default_prompt = ('''在下面的文本中，提取出所有的菜谱信息。每个菜谱的信息包括：菜谱编号、菜名、食材。
                      菜谱不包含卡路里，碳足迹、蛋白质、脂肪、碳水化合物、纤维素等信息，请你根据食材自行计算给出并放进输出的json文件而不是null。
                      请将提取出的信息以JSON格式返回，每个菜谱的信息用大括号括起来，多个菜谱之间用逗号分隔。
    Example:
    Question: 牛肉
    Context: 菜谱编号：663290，菜名：胡萝卜牛肉花卷。食材包括：主料：胡萝卜（适量）、主料：牛肉（120g）、面粉配比❤️：中筋面粉（300g）、面粉配比❤️：白糖（3g）、面粉配比❤️：酵母（3g）、面粉配比❤️：清水（170ml）、牛肉配料：盐（1g）、牛肉配料：白胡椒粉（1g）、牛肉配料：生抽（3ml）、牛肉配料：淀粉（1g）。做法步骤如下：准备主要食材：牛里脊肉馅120克，胡萝卜切碎少许，中筋面粉300克、肉馅中加盐，玉米淀粉，白胡椒粉先腌制一下，最后放食用油混合、锅中放油，肉馅炒一下盛出来备用、克面粉+3克酵母+3克白糖+170毫升清水，混合揉成光滑的面团、擀成长方形，放肉沫和胡萝卜碎，可再撒少量盐、上下对折起来、两个叠一起、从中间压一下、按照自己的手法两头卷起来，放温暖处发酵、发酵好的花卷明显变大变轻，是之前的1.5倍大，轻轻按压表面会回弹，水开后蒸锅中蒸15分钟、松软大花卷出锅了，炒熟的牛肉碎卷花卷真的很香…可以试试，孩子喜欢，我忍不住吃了两个😊。
            菜谱编号：663864，菜名：冷吃牛肉独家。食材包括：主料：牛前腿肉（一斤）、辅料：葱姜蒜（适量）、辅料：洋葱（一个）、辅料：小葱（一把）、辅料：香菜（一把）、辅料：干辣椒（半碗）、辅料：红花椒（一匙）、辅料：青花椒（一匙）、辅料：八角（3个）、辅料：香叶（3片）、调料：菜籽油（2勺）、调料：花雕酒（1匙）、调料：辣椒面（2匙）、调料：生抽（2匙）、调料：盐（小许）、调料：卤料包（一包）、调料：白糖（半匙）、调料：孜然粉（1匙）。做法步骤如下：牛前腿肉泡出血水20分钟。清洗干净、冷水下锅。加入花雕酒去腥。水开打入浮沫、加少许的盐入个底味。加入一个配置好的卤料包。八角香叶葱姜中大火把这个牛肉煮至完全熟透。是也不能煮的太软了，稍微硬一些有嚼劲、煮牛肉的时候我们来炸一个底油。菜籽油五成油温倒入葱姜蒜。香菜，洋葱，中小火把这调料炒香、干辣椒剪断，加青红花椒增香，温水浸泡，以免炸糊、锅里的这些调料全部炸成干酥炸干就把调料捞出，留底油、煮好的牛肉放置完全冷却后顺着调理切成条一定要冷却以后才好切、用手把它撕成一条一条的。我反正喜欢用手撕。这样更加入味。不喜欢的直接用刀切成切成条条、炸好的油，五成油温放入牛肉中小火。把牛肉煸至焦香，焦香、放入辣椒面。翻炒均匀、倒入泡好的辣椒，蒜和花椒倒入生抽，白糖提味、最后起锅前放入白芝麻，孜然粉。就可以啦。能够在锅里浸泡一会儿更好吃。当主食或者当零食吃都不错，可以一次多炒点儿，放真空包装。
    Answer: [{{
        "菜谱编号": 663290,
        "菜名": "胡萝卜牛肉花卷",
        "卡路里": "1000大卡",
        "碳足迹": "0.5 千克二氧化碳当量"
        "主料": [
            "胡萝卜（适量）",
            "牛肉（120g）",
            ],
        "蛋白质": "20g",
        "脂肪": "10g",
        "碳水化合物": "150g",
        "纤维素": "5g",
        "做法步骤": "准备主要食材：准备主要食材：牛里脊肉馅120克，胡萝卜切碎少许，中筋面粉300克、肉馅中加盐，玉米淀粉，白胡椒粉先腌制一下，最后放食用油混合、锅中放油，肉馅炒一下盛出来备用、克面粉+3克酵母+3克白糖+170毫升清水，混合揉成光滑的面团、擀成长方形，放肉沫和胡萝卜碎，可再撒少量盐、上下对折起来、两个叠一起、从中间压一下、按照自己的手法两头卷起来，放温暖处发酵、发酵好的花卷明显变大变轻，是之前的1.5倍大，轻轻按压表面会回弹，水开后蒸锅中蒸15分钟、松软大花卷出锅了，炒熟的牛肉碎卷花卷真的很香…可以试试，孩子喜欢，我忍不住吃了两个😊。",
    }},
    ...(省略其他菜谱)...
    {{
        "菜谱编号": 663864,
        "菜名": "冷吃牛肉独家",
        "卡路里": "800大卡",
        "碳足迹": "0.8 千克二氧化碳当量"
        "主料": [
            "牛前腿肉（一斤）",
            ],
        "蛋白质": "40g",
        "脂肪": "30g",
        "碳水化合物": "20g",
        "纤维素": "3g",
        "做法步骤": "牛前腿肉泡出血水20分钟。清洗干净、冷水下锅。加入花雕酒去腥。水开打入浮沫、加少许的盐入个底味。加入一个配置好的卤料包。八角香叶葱姜中大火把这个牛肉煮至完全熟透。是也不能煮的太软了，稍微硬一些有嚼劲、煮牛肉的时候我们来炸一个底油。菜籽油五成油温倒入葱姜蒜。香菜，洋葱，中小火把这调料炒香、干辣椒剪断，加青红花椒增香，温水浸泡，以免炸糊、锅里的这些调料全部炸成干酥炸干就把调料捞出，留底油、煮好的牛肉放置完全冷却后顺着调理切成条一定要冷却以后才好切、用手把它撕成一条一条的。我反正喜欢用手撕。这样更加入味。不喜欢的直接用刀切成切成条条、炸好的油，五成油温放入牛肉中小火。把牛肉煸至焦香，焦香、放入辣椒面。翻炒均匀、倒入泡好的辣椒，蒜和花椒倒入生抽，白糖提味、最后起锅前放入白芝麻，孜然粉。就可以啦。能够在锅里浸泡一会儿更好吃。当主食或者当零食吃都不错，可以一次多炒点儿，放真空包装。"
    }}]

    Question: {question}
    Context: {context}
    Answer:'''
    )
    pipeline_fn = build_langchain_pipeline(
        documents=sample_docs,
        default_prompt_template=default_prompt,
        keywords=keywords
    )
    # answer = pipeline_fn("主料：猪肉")
    # answer = extract_answer(answer)
    # print('____________',answer)
    # 输入关键词列表
    
    keywords = ['鸡蛋盒', '生菜', '胡萝卜', '猪肉', '嫩豆腐', '茄子']

# 存放所有结果
    all_results = []

    for kw in keywords:
        result = pipeline_fn(f"主料：{kw}")
        parsed = extract_answer(result)
        all_results.append(parsed)

# 输出所有 JSON 结果
    print('____________', all_results)


#    predictions = predict_answers(pipeline_fn, questions)


if __name__ == "__main__":
    # 运行主函数
    smart_fridge_RAG()
    # 运行测试函数
    # test_smart_fridge_RAG()