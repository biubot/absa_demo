<template>
  <div class="sentiment-analysis-container">
    <!-- 左侧边栏-->
    <div class="sidebar">
      <h3>分析模式</h3>
      <ul class="mode-list">
        <li :class="{ active: activeMode === 'multiAspect' }" @click="switchMode('multiAspect')">多方面情感分析</li>
        <li :class="{ active: activeMode === 'sentence' }" @click="switchMode('sentence')">句子情感分析</li>
        <li :class="{ active: activeMode === 'document' }" @click="switchMode('document')">篇章级别情感分析</li>
      </ul>
    </div>

    <!-- 中间内容 -->
    <div class="main-content">
      <h2 class="page-title">
        {{ getModeTitle() }}
      </h2>

      <!-- 多方面情感分析内容 -->
      <div v-if="activeMode === 'multiAspect'">
        <!-- 模型选择 -->
        <div class="model-selection">
          <label for="model">选择模型：</label>
          <select id="model" v-model="selectedModel">
            <option v-for="model in models" :key="model.value" :value="model.value">
              {{ model.label }}
            </option>
          </select>
        </div>

        <!-- 文本输入 -->
        <div class="text-input">
          <label for="multiAspectText">输入文本：</label>
          <textarea
            id="multiAspectText"
            v-model="multiAspectText"
            placeholder="请输入要分析的文本内容..."
            rows="6"
          ></textarea>
        </div>

        <!-- 方面词输入 -->
        <div class="aspect-input">
          <label for="aspects">输入方面词：</label>
          <div class="aspect-input-container">
            <input
              type="text"
              v-model="newAspect"
              placeholder="输入方面词，多个方面词用逗号分隔"
              @keyup.enter="addAspects"
            />
            <button class="add-aspect-btn" @click="addAspects" :disabled="!newAspect.trim()">
              添加
            </button>
          </div>
          <div class="aspect-hint">
            提示：可输入多个方面词，用逗号分隔，如"service, food, quality"
          </div>
          <div class="aspect-tags input-tags" v-if="aspectList.length > 0">
            <div
              v-for="(aspect, index) in aspectList"
              :key="index"
              class="aspect-tag input-tag"
            >
              {{ aspect }}
              <span class="remove-tag" @click="removeAspect(index)">×</span>
            </div>
          </div>
          <div class="aspect-hint warning" v-else>
            请添加至少一个方面词进行多方面情感分析
          </div>
        </div>

        <!-- 提交按钮 -->
        <button
          class="analyze-btn"
          @click="analyzeSentiment"
          :disabled="!multiAspectText.trim() || aspectList.length === 0 || isLoading"
        >
          {{ isLoading ? '分析中...' : '开始分析' }}
        </button>
      </div>

      <!-- 句子情感分析内容 -->
      <div v-if="activeMode === 'sentence'">
        <!-- 文本输入 -->
        <div class="text-input">
          <label for="sentenceText">输入文本：</label>
          <textarea
            id="sentenceText"
            v-model="sentenceText"
            placeholder="请输入要进行句子情感分析的文本..."
            rows="6"
          ></textarea>
        </div>

        <!-- 提交按钮 -->
        <button
          class="analyze-btn"
          @click="analyzeSentiment"
          :disabled="!sentenceText.trim() || isLoading"
        >
          {{ isLoading ? '分析中...' : '开始分析' }}
        </button>
      </div>

      <!-- 篇章级别情感分析内容 -->
      <div v-if="activeMode === 'document'">
        <!-- 文本输入 -->
        <div class="text-input">
          <label for="documentText">输入文本：</label>
          <textarea
            id="documentText"
            v-model="documentText"
            placeholder="请输入要进行篇章级别情感分析的文本..."
            rows="6"
          ></textarea>
        </div>

        <!-- 提交按钮 -->
        <button
          class="analyze-btn"
          @click="analyzeSentiment"
          :disabled="!documentText.trim() || isLoading"
        >
          {{ isLoading ? '分析中...' : '开始分析' }}
        </button>
      </div>

      <!-- 结果显示区域 -->
      <div class="results" v-if="analysisResults">
        <h3>分析结果</h3>

        <div class="result-section">
          <h4>原始文本：</h4>
          <p>{{ analysisResults.original_text }}</p>
        </div>

        <!-- 多方面情感分析结果 -->
        <template v-if="activeMode === 'multiAspect'">
          <div class="result-section">
            <h4>方面词：</h4>
            <div class="aspect-tags">
              <span
                v-for="(aspect, index) in analysisResults.aspects"
                :key="index"
                class="aspect-tag"
              >
                {{ aspect }}
              </span>
            </div>
          </div>

          <!-- 情感极性结果区域 -->
          <div class="result-section">
            <h4>情感极性：</h4>
            <div class="sentiment-results">
              <div v-if="analysisResults.sentiment_results" class="sentiment-table">
                <div class="sentiment-row header">
                  <div class="aspect-cell">方面词</div>
                  <div class="sentiment-cell">积极</div>
                  <div class="sentiment-cell">消极</div>
                  <div class="sentiment-cell">中性</div>
                  <div class="sentiment-cell">情感结果</div>
                </div>
                <div
                  v-for="(sentiment, aspect) in analysisResults.sentiment_results"
                  :key="aspect"
                  class="sentiment-row"
                >
                  <div class="aspect-cell">{{ aspect }}</div>
                  <div class="sentiment-cell positive">{{ sentiment.positive > 0 ? "✓" : "-" }}</div>
                  <div class="sentiment-cell negative">{{ sentiment.negative > 0 ? "✓" : "-" }}</div>
                  <div class="sentiment-cell neutral">{{ sentiment.neutral > 0 ? "✓" : "-" }}</div>
                  <div class="sentiment-cell result">
                    <span v-if="sentiment.positive > 0" class="positive">积极</span>
                    <span v-else-if="sentiment.negative > 0" class="negative">消极</span>
                    <span v-else class="neutral">中性</span>
                  </div>
                </div>
              </div>
              <p v-else class="placeholder-text">暂无情感分析结果</p>
            </div>
          </div>
        </template>

        <!-- 句子情感分析结果 -->
        <template v-if="activeMode === 'sentence'">
          <div class="result-section">
            <h4>句子情感分析结果：</h4>
            <div class="sentiment-results">
              <div v-if="analysisResults.sentence_results" class="sentiment-table">
                <div class="sentiment-row header">
                  <div class="aspect-cell">句子</div>
                  <div class="sentiment-cell">情感极性</div>
                  <div class="sentiment-cell">置信度</div>
                </div>
                <div
                  v-for="(result, index) in analysisResults.sentence_results"
                  :key="index"
                  class="sentiment-row"
                >
                  <div class="aspect-cell">{{ result.sentence }}</div>
                  <div class="sentiment-cell result">
                    <span :class="getSentimentClass(result.sentiment)">
                      {{ getSentimentText(result.sentiment) }}
                    </span>
                  </div>
                  <div class="sentiment-cell">{{ (result.confidence * 100).toFixed(1) }}%</div>
                </div>
              </div>
              <p v-else class="placeholder-text">暂无句子情感分析结果</p>
            </div>
          </div>
        </template>

        <!-- 篇章级别情感分析结果 -->
        <template v-if="activeMode === 'document'">
          <div class="result-section">
            <h4>篇章情感分析结果：</h4>
            <div class="sentiment-results document-result">
              <div v-if="analysisResults.document_sentiment" class="document-sentiment">
                <div class="sentiment-summary">
                  <div class="sentiment-score">
                    <span class="label">整体情感：</span>
                    <span :class="getSentimentClass(analysisResults.document_sentiment.overall)">
                      {{ getSentimentText(analysisResults.document_sentiment.overall) }}
                    </span>
                  </div>
                  <div class="sentiment-distribution">
                    <div class="distribution-item">
                      <span class="label">积极：</span>
                      <span class="value positive">{{ (analysisResults.document_sentiment.positive * 100).toFixed(1) }}%</span>
                      <div class="progress-bar">
                        <div class="progress positive" :style="{ width: (analysisResults.document_sentiment.positive * 100) + '%' }"></div>
                      </div>
                    </div>
                    <div class="distribution-item">
                      <span class="label">消极：</span>
                      <span class="value negative">{{ (analysisResults.document_sentiment.negative * 100).toFixed(1) }}%</span>
                      <div class="progress-bar">
                        <div class="progress negative" :style="{ width: (analysisResults.document_sentiment.negative * 100) + '%' }"></div>
                      </div>
                    </div>
                    <div class="distribution-item">
                      <span class="label">中性：</span>
                      <span class="value neutral">{{ (analysisResults.document_sentiment.neutral * 100).toFixed(1) }}%</span>
                      <div class="progress-bar">
                        <div class="progress neutral" :style="{ width: (analysisResults.document_sentiment.neutral * 100) + '%' }"></div>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="summary-section">
                  <h4>情感摘要：</h4>
                  <p>{{ analysisResults.document_sentiment.summary }}</p>
                </div>
              </div>
              <p v-else class="placeholder-text">暂无篇章情感分析结果</p>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SentimentAnalysis',
  data() {
    return {
      activeMode: 'multiAspect',
      models: [
        { label: 'PHNN model', value: 'phnnmodel' },
        { label: 'GCNBERT model', value: 'gcnbertmodel' },
        { label: 'old model', value: 'oldmodel' }
      ],
      selectedModel: 'phnnmodel',
      multiAspectText: '',   // 多方面情感分析的文本
      sentenceText: '',      // 句子情感分析的文本
      documentText: '',      // 篇章级别情感分析的文本
      aspectList: [],
      newAspect: '',
      isLoading: false,
      analysisResults: null
    };
  },
  methods: {
    getModeTitle() {
      switch (this.activeMode) {
        case 'multiAspect':
          return '多方面情感分析';
        case 'sentence':
          return '句子情感分析';
        case 'document':
          return '篇章级别情感分析';
        default:
          return '情感分析';
      }
    },

    switchMode(mode) {
      this.activeMode = mode;
      this.analysisResults = null;
    },

    addAspects() {
      const aspectInput = this.newAspect.trim();
      if (!aspectInput) return;

      const newAspects = aspectInput.split(/[,，]/)
        .map(aspect => aspect.trim())
        .filter(aspect => aspect !== '');

      newAspects.forEach(aspect => {
        if (!this.aspectList.includes(aspect)) {
          this.aspectList.push(aspect);
        }
      });

      this.newAspect = '';
    },

    removeAspect(index) {
      this.aspectList.splice(index, 1);
    },

    getSentimentClass(sentiment) {
      if (typeof sentiment === 'string') {
        if (sentiment === 'positive') return 'positive';
        if (sentiment === 'negative') return 'negative';
        return 'neutral';
      } else {
        if (sentiment > 0) return 'positive';
        if (sentiment < 0) return 'negative';
        return 'neutral';
      }
    },

    getSentimentText(sentiment) {
      if (typeof sentiment === 'string') {
        if (sentiment === 'positive') return '积极';
        if (sentiment === 'negative') return '消极';
        return '中性';
      } else {
        if (sentiment > 0) return '积极';
        if (sentiment < 0) return '消极';
        return '中性';
      }
    },

    async analyzeSentiment() {
      // 根据当前模式获取对应的文本
      let text = '';
      switch (this.activeMode) {
        case 'multiAspect':
          text = this.multiAspectText;
          if (!text.trim() || this.aspectList.length === 0) return;
          break;
        case 'sentence':
          text = this.sentenceText;
          if (!text.trim()) return;
          break;
        case 'document':
          text = this.documentText;
          if (!text.trim()) return;
          break;
      }

      this.isLoading = true;

      try {
        // 构建请求数据，对所有模式都包含必要的信息
        const requestData = {
          text: text,
          mode: this.activeMode
        };

        // 针对多方面情感分析，添加特定字段
        if (this.activeMode === 'multiAspect') {
          requestData.model = this.selectedModel;
          requestData.aspects = this.aspectList;
        }

        // 发送请求到后端API
        const response = await fetch('http://localhost:8080/api/sentiment-analysis', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestData)
        });

        if (!response.ok) {
          throw new Error('网络请求失败');
        }

        // 获取并设置分析结果
        this.analysisResults = await response.json();
      } catch (error) {
        console.error('情感分析请求失败:', error);
        alert('分析失败，请稍后再试');
      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

<style scoped>
.sentiment-analysis-container {
  display: flex;
  height: 100vh;
  background-color: #f5f7fa;
}

.sidebar {
  width: 200px;
  background-color: #334155;
  color: white;
  padding: 20px 0;
}

.sidebar h3 {
  padding: 0 20px;
  margin-bottom: 15px;
}

.mode-list {
  list-style-type: none;
  padding: 0;
}

.mode-list li {
  padding: 12px 20px;
  cursor: pointer;
  transition: background-color 0.3s, border-left 0.3s;
}

.mode-list li:hover {
  background-color: #475569;
}

.mode-list li.active {
  background-color: #1e293b;
  border-left: 4px solid #3b82f6;
}

.main-content {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
}

.page-title {
  text-align: center;
  margin-bottom: 30px;
  color: #1e293b;
  font-size: 28px;
}

.model-selection, .text-input, .aspect-input {
  margin-bottom: 20px;
}

.model-selection label, .text-input label, .aspect-input label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

select, textarea, input {
  width: 100%;
  padding: 10px;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  font-size: 16px;
}

textarea {
  resize: vertical;
}

.aspect-input-container {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.aspect-input-container input {
  flex: 1;
}

.add-aspect-btn {
  padding: 0 15px;
  background-color: #64748b;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.add-aspect-btn:hover:not(:disabled) {
  background-color: #475569;
}

.add-aspect-btn:disabled {
  background-color: #94a3b8;
  cursor: not-allowed;
}

.aspect-hint {
  color: #64748b;
  font-size: 14px;
  margin-top: 8px;
  margin-bottom: 12px;
}

.aspect-hint.warning {
  color: #f59e0b;
}

.input-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 15px;
}

.input-tag {
  display: inline-flex;
  align-items: center;
  background-color: #e2e8f0;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 14px;
}

.remove-tag {
  margin-left: 5px;
  cursor: pointer;
  font-weight: bold;
  font-size: 16px;
}

.remove-tag:hover {
  color: #ef4444;
}

.analyze-btn {
  padding: 12px 24px;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
  display: block;
  margin: 30px auto;
  min-width: 200px;
}

.analyze-btn:hover:not(:disabled) {
  background-color: #2563eb;
}

.analyze-btn:disabled {
  background-color: #93c5fd;
  cursor: not-allowed;
}

.results {
  margin-top: 30px;
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.result-section {
  margin-bottom: 20px;
}

.result-section h4 {
  margin-bottom: 10px;
  color: #334155;
}

.aspect-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.aspect-tag {
  background-color: #e2e8f0;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 14px;
}

.sentiment-results {
  padding: 15px;
  background-color: #f8fafc;
  border-radius: 4px;
  border: 1px dashed #cbd5e1;
}

.placeholder-text {
  color: #64748b;
  font-style: italic;
  text-align: center;
}

.sentiment-table {
  width: 100%;
  border-collapse: collapse;
}

.sentiment-row {
  display: flex;
  border-bottom: 1px solid #e2e8f0;
}

.sentiment-row.header {
  font-weight: bold;
  background-color: #f1f5f9;
}

.aspect-cell, .sentiment-cell {
  padding: 10px;
  flex: 1;
  text-align: center;
}

.aspect-cell {
  flex: 2;
  text-align: left;
}

.positive {
  color: #10b981;
}

.negative {
  color: #ef4444;
}

.neutral {
  color: #6b7280;
}

.sentiment-cell.result {
  font-weight: bold;
}

.document-sentiment {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sentiment-summary {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.sentiment-score {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
  padding: 10px;
  background-color: #f1f5f9;
  border-radius: 4px;
}

.sentiment-score .label {
  margin-right: 10px;
}

.sentiment-distribution {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.distribution-item {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.distribution-item .label {
  width: 60px;
  font-weight: 500;
}

.distribution-item .value {
  width: 60px;
  text-align: right;
  font-weight: 500;
}

.progress-bar {
  flex: 1;
  height: 12px;
  background-color: #e2e8f0;
  border-radius: 6px;
  margin-left: 10px;
  overflow: hidden;
}

.progress {
  height: 100%;
  border-radius: 6px;
}

.progress.positive {
  background-color: #10b981;
}

.progress.negative {
  background-color: #ef4444;
}

.progress.neutral {
  background-color: #6b7280;
}

.summary-section {
  background-color: #f1f5f9;
  padding: 15px;
  border-radius: 4px;
}

.summary-section h4 {
  margin-top: 0;
  margin-bottom: 10px;
}

.summary-section p {
  margin: 0;
  line-height: 1.6;
}
</style>