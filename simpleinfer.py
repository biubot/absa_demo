import re
import numpy as np
from typing import Dict, List, Tuple, Union, Optional


class SentimentAnalyzer:
    """
    情感分析器基类，提供句子级和篇章级情感分析功能
    """

    def __init__(self):
        # 积极情感词典
        self.positive_words = {
            '喜欢', '好', '棒', '优秀', '满意', '推荐', '优质', '精彩', '赞', '不错',
            '完美', '惊艳', '舒适', '实用', '便宜', '划算', '值得', '高效', '友好',
            '热情', '专业', '细致', '耐心', '周到', '贴心', '快速', '准时', '可靠',
            '新鲜', '干净', '整洁', '美味', '丰富', '出色', '卓越', '高档', '高端',
            '顺畅', '简单', '方便', '愉快', '享受', '精致', '超值', '优惠', '善良',
            '温和', '亲切', '诚恳', '礼貌', '热心', '满足', '放心', '安心', '合适'
        }

        # 消极情感词典
        self.negative_words = {
            '差', '糟糕', '失望', '不满', '难吃', '难用', '难受', '贵', '慢', '等待',
            '浪费', '无聊', '枯燥', '乏味', '不足', '缺乏', '缺点', '问题', '错误',
            '故障', '坏', '破', '旧', '脏', '累', '麻烦', '复杂', '困难', '不便',
            '昂贵', '不值', '不好', '薄', '硬', '冷', '热', '吵', '吵闹', '拥挤',
            '挤', '小', '窄', '短', '低', '慢', '拖延', '不专业', '不耐心', '敷衍',
            '态度差', '服务差', '质量差', '水平低', '一般', '马虎', '粗心', '不详细',
            '不全面', '不准确', '不及时', '不卫生', '不干净', '不新鲜', '不友好'
        }

        # 否定词表
        self.negation_words = {
            '不', '没', '没有', '不是', '不能', '不要', '不可', '无', '莫', '非',
            '别', '勿', '未', '毫无', '并非', '决不', '不曾', '并未', '绝不', '从不',
            '不必', '无须', '并没', '不太', '不怎么', '不大', '不会', '不可能'
        }

        # 程度副词，用于增强或减弱情感强度
        self.degree_words = {
            # 极其 (程度最高)
            '极': 2.0, '极其': 2.0, '极度': 2.0, '极端': 2.0, '截然': 2.0,
            '完全': 2.0, '绝对': 2.0, '最': 2.0,

            # 很 (程度较高)
            '很': 1.5, '太': 1.5, '非常': 1.5, '特别': 1.5, '相当': 1.5,
            '十分': 1.5, '格外': 1.5, '分外': 1.5, '尤其': 1.5, '更加': 1.5,

            # 较 (程度一般)
            '比较': 1.25, '较': 1.25, '略': 1.25, '稍': 1.25, '稍微': 1.25,
            '多': 1.25, '略微': 1.25, '略为': 1.25, '有点': 1.25, '有些': 1.25,

            # 一点点 (程度较低)
            '一点': 1.1, '一点点': 1.1, '有一点点': 1.1, '些许': 1.1, '少许': 1.1,
        }

    def _clean_text(self, text: str) -> str:
        """清理文本，去除不必要的字符"""
        # 去除多余空白
        text = re.sub(r'\s+', ' ', text)
        # 去除特殊标点
        text = re.sub(r'[""【】「」『』《》〈〉\(\)\[\]]', '', text)
        return text.strip()

    def _split_sentences(self, text: str) -> List[str]:
        """将文本分割成句子列表"""
        # 使用正则表达式按照常见句子分隔符分割文本
        sentences = re.split(r'[。！？!?;；]+', text)
        # 过滤掉空字符串
        return [sent.strip() for sent in sentences if sent.strip()]

    def _calculate_sentence_sentiment(self, sentence: str) -> Tuple[float, float]:
        """
        计算单个句子的情感分数

        返回：(分数, 置信度) - 分数范围[-1,1]，置信度范围[0,1]
        """
        sentence = self._clean_text(sentence)
        words = list(sentence)  # 中文按字符分割

        # 情感基础分值
        sentiment_score = 0

        # 匹配到的情感词数量
        emotion_word_count = 0

        # 记录上一个情感词的位置和极性
        last_emotion_pos = -1
        last_emotion_polarity = 0  # 0表示中性，1表示积极，-1表示消极

        # 记录当前否定词的影响范围
        negation_influence = 1  # 1表示没有否定词，-1表示有否定词

        # 当前程度词的增强系数
        degree_multiplier = 1.0

        # 遍历句子中可能的n-gram词组(最多考虑4字词)
        for i in range(len(words)):
            # 检查否定词
            for neg_len in range(min(4, len(words) - i), 0, -1):
                if ''.join(words[i:i + neg_len]) in self.negation_words:
                    negation_influence = -1
                    break

            # 检查程度词
            for deg_len in range(min(4, len(words) - i), 0, -1):
                word = ''.join(words[i:i + deg_len])
                if word in self.degree_words:
                    degree_multiplier = self.degree_words[word]
                    break

            # 检查情感词
            word_found = False
            for word_len in range(min(4, len(words) - i), 0, -1):
                word = ''.join(words[i:i + word_len])

                if word in self.positive_words:
                    word_found = True
                    emotion_word_count += 1
                    # 计算情感分值
                    sentiment_score += 1 * negation_influence * degree_multiplier

                    # 重置否定词和程度词
                    negation_influence = 1
                    degree_multiplier = 1.0

                    last_emotion_pos = i
                    last_emotion_polarity = 1 * negation_influence
                    break

                elif word in self.negative_words:
                    word_found = True
                    emotion_word_count += 1
                    # 计算情感分值
                    sentiment_score += -1 * negation_influence * degree_multiplier

                    # 重置否定词和程度词
                    negation_influence = 1
                    degree_multiplier = 1.0

                    last_emotion_pos = i
                    last_emotion_polarity = -1 * negation_influence
                    break

            if word_found:
                # 跳过已经匹配的词
                i += word_len - 1

        # 如果没有情感词，返回中性(0)分值，低置信度
        if emotion_word_count == 0:
            return 0, 0.5

        # 归一化情感分值到[-1,1]范围
        if sentiment_score != 0:
            normalized_score = sentiment_score / (emotion_word_count * 2)  # *2是考虑到程度词可能的放大效果
            normalized_score = max(-1, min(1, normalized_score))  # 确保在[-1,1]范围内
        else:
            normalized_score = 0

        # 计算置信度，与情感词数量和句子长度有关
        confidence = min(0.5 + (emotion_word_count / len(words) * 0.5), 0.95)

        return normalized_score, confidence

    def analyze_sentence(self, sentence: str) -> Dict:
        """
        分析单个句子的情感

        返回：
        {
            'sentence': 原句,
            'sentiment': 情感极性('positive'/'negative'/'neutral'),
            'score': 情感分数(-1到1),
            'confidence': 置信度(0到1)
        }
        """
        score, confidence = self._calculate_sentence_sentiment(sentence)

        # 确定情感极性
        if score > 0.1:
            sentiment = 'positive'
        elif score < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'

        return {
            'sentence': sentence,
            'sentiment': sentiment,
            'score': score,
            'confidence': confidence
        }

    def analyze_sentences(self, text: str) -> List[Dict]:
        """
        对文本进行句子级情感分析

        返回：
        [
            {
                'sentence': 句子1,
                'sentiment': 情感极性,
                'score': 情感分数,
                'confidence': 置信度
            },
            ...
        ]
        """
        sentences = self._split_sentences(text)
        results = []

        for sentence in sentences:
            if not sentence:
                continue
            result = self.analyze_sentence(sentence)
            results.append(result)

        return results

    def analyze_document(self, text: str) -> Dict:
        """
        对整个文档进行情感分析

        返回：
        {
            'overall': 整体情感极性,
            'positive': 积极情感比例,
            'negative': 消极情感比例,
            'neutral': 中性情感比例,
            'summary': 分析摘要
        }
        """
        # 首先进行句子级分析
        sentence_results = self.analyze_sentences(text)

        if not sentence_results:
            return {
                'overall': 'neutral',
                'positive': 0.33,
                'negative': 0.33,
                'neutral': 0.34,
                'summary': '文本太短或无法分析，无法确定情感倾向。'
            }

        # 统计各情感类型的数量和分数
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        total_score = 0
        weighted_score = 0
        total_confidence = 0

        for result in sentence_results:
            sentiment = result['sentiment']
            score = result['score']
            confidence = result['confidence']

            sentiment_counts[sentiment] += 1
            total_score += score
            weighted_score += score * confidence
            total_confidence += confidence

        # 计算情感比例
        total_sentences = len(sentence_results)
        positive_ratio = sentiment_counts['positive'] / total_sentences
        negative_ratio = sentiment_counts['negative'] / total_sentences
        neutral_ratio = sentiment_counts['neutral'] / total_sentences

        # 计算加权平均情感分数
        if total_confidence > 0:
            avg_weighted_score = weighted_score / total_confidence
        else:
            avg_weighted_score = 0

        # 确定整体情感
        if avg_weighted_score > 0.1:
            overall = 'positive'
        elif avg_weighted_score < -0.1:
            overall = 'negative'
        else:
            overall = 'neutral'

        # 生成摘要
        pos_percent = round(positive_ratio * 100, 1)
        neg_percent = round(negative_ratio * 100, 1)
        neu_percent = round(neutral_ratio * 100, 1)

        # 构建摘要内容
        if overall == 'positive':
            main_sentiment = f"文本整体情感倾向为积极，积极情感占比{pos_percent}%"
        elif overall == 'negative':
            main_sentiment = f"文本整体情感倾向为消极，消极情感占比{neg_percent}%"
        else:
            main_sentiment = f"文本整体情感倾向为中性，中性情感占比{neu_percent}%"

        # 添加句子情感分布
        distribution = f"其中积极情感占比{pos_percent}%，消极情感占比{neg_percent}%，中性情感占比{neu_percent}%"

        # 如果有明显的主导情感，增加描述
        if positive_ratio > 0.6:
            conclusion = "文本表现出明显的积极情感。"
        elif negative_ratio > 0.6:
            conclusion = "文本表现出明显的消极情感。"
        elif neutral_ratio > 0.6:
            conclusion = "文本情感表达较为中性。"
        elif positive_ratio > negative_ratio and positive_ratio > neutral_ratio:
            conclusion = "文本偏向积极情感，但也包含其他情感表达。"
        elif negative_ratio > positive_ratio and negative_ratio > neutral_ratio:
            conclusion = "文本偏向消极情感，但也包含其他情感表达。"
        else:
            conclusion = "文本情感表达复杂，包含多种情感。"

        summary = f"{main_sentiment}。{distribution}。{conclusion}"

        return {
            'overall': overall,
            'positive': positive_ratio,
            'negative': negative_ratio,
            'neutral': neutral_ratio,
            'summary': summary
        }


# 创建单例实例
_analyzer_instance = None


def get_analyzer():
    """获取情感分析器实例（单例模式）"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = SentimentAnalyzer()
    return _analyzer_instance