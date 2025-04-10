from flask import Flask, request, jsonify
from flask_cors import CORS
from ABSA.infer import load_phnn_inferer
from ABSA_old.infer import load_old_inferer
from ABSA_GCN.infer import load_gcn_inferer
from simpleinfer import get_analyzer

app = Flask(__name__)
CORS(app)

phnn_inferer = load_phnn_inferer()
old_inferer = load_old_inferer()
gcn_inferer = load_gcn_inferer()
# 获取情感分析器实例
sentiment_analyzer = get_analyzer()


@app.route('/api/sentiment-analysis', methods=['POST'])
def sentiment_analysis():
    # 获取请求数据
    data = request.json
    if not data:
        return jsonify({"error": "没有接收到数据"}), 400

    # 提取数据
    text = data.get('text', '')
    mode = data.get('mode', 'multiAspect')  # 默认为多方面情感分析
    model_name = data.get('model', '')
    aspects = data.get('aspects', [])

    # 根据不同的模式处理
    if mode == 'multiAspect':
        print(f'加载模型: {model_name} ...')
        print(f"接收到的模型: {model_name}")
        print(f"接收到的文本: {text}")
        print(f"接收到的方面词: {aspects}")

        sentiment_results = {}
        for aspect in aspects:
            if model_name == "phnnmodel":
                sentiment = phnn_inferer.evaluate(text, aspect)
            elif model_name == "gcnbertmodel":
                sentiment = gcn_inferer.evaluate(text, aspect)
            elif model_name == "oldmodel":
                sentiment = old_inferer.evaluate(text, aspect)

            print(f"方面词 {aspect} 的情感值: {sentiment}")
            positive = 1.0 if sentiment == 1 else 0.0
            negative = 1.0 if sentiment == -1 else 0.0
            neutral = 1.0 if sentiment == 0 else 0.0

            sentiment_results[aspect] = {
                "positive": positive,
                "negative": negative,
                "neutral": neutral,
            }

        # 构建响应数据
        response = {
            "original_text": text,
            "aspects": aspects,
            "model_used": model_name,
            "sentiment_results": sentiment_results
        }

    elif mode == 'sentence':
        # 使用我们的句子情感分析
        sentence_results = sentiment_analyzer.analyze_sentences(text)
        response = {
            "original_text": text,
            "sentence_results": sentence_results
        }

    elif mode == 'document':
        # 使用我们的篇章情感分析
        document_sentiment = sentiment_analyzer.analyze_document(text)
        response = {
            "original_text": text,
            "document_sentiment": document_sentiment
        }

    else:
        return jsonify({"error": "不支持的分析模式"}), 400

    return jsonify(response)


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "服务正常运行"})


if __name__ == '__main__':
    # 在开发环境中使用debug模式
    app.run(host='127.0.0.1', port=8080, debug=True)