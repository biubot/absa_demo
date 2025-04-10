<template>
  <div class="sentiment-app">
    <!-- 左侧边栏：分析模式选择 -->
    <div class="sidebar">
      <h2>分析模式</h2>
      <ul class="mode-list">
        <li
          v-for="(mode, index) in analysisModes"
          :key="index"
          :class="{ active: selectedMode === mode.id }"
          @click="selectedMode = mode.id"
        >
          {{ mode.name }}
        </li>
      </ul>
    </div>

    <!-- 中间内容区域 -->
    <div class="content">
      <h1>情感分析系统</h1>

      <div class="analysis-panel">
        <div class="mode-title">
          <h2>{{ getCurrentMode().name }}</h2>
          <p>{{ getCurrentMode().description }}</p>
        </div>

        <!-- 模型选择 -->
        <div class="model-selection">
          <h3>选择模型</h3>
          <select v-model="selectedModel">
            <option v-for="model in models" :key="model.id" :value="model.id">
              {{ model.name }}
            </option>
          </select>
          <p class="model-description">{{ getModelDescription() }}</p>
        </div>

        <!-- 输入区域 -->
        <div class="input-area">
          <h3>输入文本</h3>
          <textarea
            v-model="inputText"
            placeholder="请输入需要分析的文本..."
            rows="6"
          ></textarea>

          <!-- 多方面分析时的方面选择 -->
          <div v-if="selectedMode === 'multi-aspect'" class="aspects-selection">
            <h3>选择分析方面</h3>
            <div class="aspects-grid">
              <label v-for="aspect in aspects" :key="aspect.id" class="aspect-checkbox">
                <input type="checkbox" v-model="selectedAspects" :value="aspect.id">
                {{ aspect.name }}
              </label>
            </div>
          </div>

          <!-- 分析按钮 -->
          <div class="action-buttons">
            <button
              class="analyze-btn"
              @click="startAnalysis"
              :disabled="!inputText || isAnalyzing"
            >
              {{ isAnalyzing ? '分析中...' : '开始分析' }}
            </button>
          </div>
        </div>

        <!-- 新的三框结果展示区域 -->
        <div v-if="analysisResult" class="three-box-result">
          <div class="result-box">
            <h3>原文本</h3>
            <div class="box-content">{{ inputText }}</div>
          </div>

          <div class="result-box">
            <h3>方面词</h3>
            <div class="box-content">
              <span v-for="(aspectWord, index) in analysisResult.aspectWords" :key="index" class="aspect-word">
                {{ aspectWord }}
              </span>
            </div>
          </div>

          <div class="result-box">
            <h3>情感极性</h3>
            <div class="box-content">
              <div class="polarity-item" :class="getSentimentClass(analysisResult.overall)">
                整体情感: {{ getSentimentLabel(analysisResult.overall) }}
              </div>
              <div v-if="selectedMode === 'multi-aspect'">
                <div
                  v-for="(score, aspect) in analysisResult.aspects"
                  :key="aspect"
                  class="polarity-item"
                  :class="getSentimentClass(score)"
                >
                  {{ getAspectName(aspect) }}: {{ getSentimentLabel(score) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 原有结果展示区域（保留但根据模式展示） -->
        <div v-if="analysisResult && selectedMode !== 'overall'" class="result-area">
          <h3>详细分析结果</h3>

          <div v-if="selectedMode === 'multi-aspect'" class="aspect-results">
            <div v-for="(score, aspect) in analysisResult.aspects" :key="aspect" class="aspect-item">
              <div class="aspect-name">{{ getAspectName(aspect) }}</div>
              <div class="aspect-score" :class="getSentimentClass(score)">
                {{ getSentimentLabel(score) }}
              </div>
              <div class="score-bar">
                <div class="score-fill" :style="{ width: (score + 1) * 50 + '%' }"></div>
              </div>
            </div>
          </div>

          <div v-if="selectedMode === 'emotional'" class="emotion-results">
            <div class="emotion-chart">
              <div v-for="(value, emotion) in analysisResult.emotions" :key="emotion" class="emotion-bar">
                <div class="emotion-label">{{ emotion }}</div>
                <div class="emotion-value-bar" :style="{ width: value * 100 + '%' }"></div>
                <div class="emotion-value">{{ (value * 100).toFixed(1) }}%</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SentimentAnalysis',
  data() {
    return {
      // 分析模式
      analysisModes: [
        { id: 'overall', name: '整体情感分析', description: '分析文本的整体情感倾向，判断是积极、中性还是消极。' },
        { id: 'multi-aspect', name: '多方面情感分析', description: '从多个角度分析文本中的情感，如产品的价格、质量、服务等方面。' },
        { id: 'emotional', name: '情绪分析', description: '检测文本中表达的情绪类型，如喜悦、愤怒、悲伤、恐惧等。' },
        { id: 'trend', name: '情感趋势分析', description: '分析一段时间内情感的变化趋势。' }
      ],
      selectedMode: 'overall',

      // 模型列表
      models: [
        { id: 'basic', name: '基础情感分析模型', description: '适用于一般文本的简单情感分析' },
        { id: 'advanced', name: '高级情感分析模型', description: '提供更精确的情感分析结果，支持多语言' },
        { id: 'bert', name: 'BERT情感分析模型', description: '基于BERT的深度学习模型，更好地理解上下文' },
        { id: 'xlnet', name: 'XLNet情感分析模型', description: '基于XLNet的深度学习模型，适合复杂情感表达' }
      ],
      selectedModel: 'basic',

      // 多方面分析的方面列表
      aspects: [
        { id: 'price', name: '价格' },
        { id: 'quality', name: '质量' },
        { id: 'service', name: '服务' },
        { id: 'usability', name: '易用性' },
        { id: 'design', name: '设计' },
        { id: 'performance', name: '性能' }
      ],
      selectedAspects: ['price', 'quality', 'service'],

      // 用户输入
      inputText: '',

      // 分析状态和结果
      isAnalyzing: false,
      analysisResult: null
    };
  },
  methods: {
    // 获取当前选择的分析模式
    getCurrentMode() {
      return this.analysisModes.find(mode => mode.id === this.selectedMode) || this.analysisModes[0];
    },

    // 获取当前选择的模型描述
    getModelDescription() {
      const model = this.models.find(model => model.id === this.selectedModel);
      return model ? model.description : '';
    },

    // 获取方面名称
    getAspectName(aspectId) {
      const aspect = this.aspects.find(a => a.id === aspectId);
      return aspect ? aspect.name : aspectId;
    },

    // 根据情感得分返回对应的CSS类名
    getSentimentClass(score) {
      if (score > 0.3) return 'positive';
      if (score < -0.3) return 'negative';
      return 'neutral';
    },

    // 根据情感得分返回对应的文本标签
    getSentimentLabel(score) {
      if (score > 0.7) return '非常正面';
      if (score > 0.3) return '正面';
      if (score > -0.3) return '中性';
      if (score > -0.7) return '负面';
      return '非常负面';
    },

    // 开始分析
    startAnalysis() {
      if (!this.inputText) return;

      this.isAnalyzing = true;

      // 模拟API调用，实际项目中应该调用后端API
      setTimeout(() => {
        // 模拟方面词提取（实际应由后端分析）
        const randomAspectWords = ['价格', '质量', '体验', '服务', '功能', '设计'];
        const aspectWords = [];
        // 随机选择2-4个方面词
        const wordCount = Math.floor(Math.random() * 3) + 2;
        for (let i = 0; i < wordCount; i++) {
          const randomIndex = Math.floor(Math.random() * randomAspectWords.length);
          if (!aspectWords.includes(randomAspectWords[randomIndex])) {
            aspectWords.push(randomAspectWords[randomIndex]);
          }
        }

        // 根据不同的分析模式返回不同结构的模拟数据
        if (this.selectedMode === 'overall') {
          this.analysisResult = {
            overall: Math.random() * 2 - 1, // -1到1之间的随机值
            aspectWords: aspectWords
          };
        } else if (this.selectedMode === 'multi-aspect') {
          const aspects = {};
          this.selectedAspects.forEach(aspect => {
            aspects[aspect] = Math.random() * 2 - 1;
          });
          this.analysisResult = {
            overall: Math.random() * 2 - 1,
            aspects: aspects,
            aspectWords: aspectWords
          };
        } else if (this.selectedMode === 'emotional') {
          this.analysisResult = {
            overall: Math.random() * 2 - 1,
            emotions: {
              '喜悦': Math.random(),
              '愤怒': Math.random() * 0.5,
              '悲伤': Math.random() * 0.7,
              '恐惧': Math.random() * 0.3,
              '惊讶': Math.random() * 0.6,
              '厌恶': Math.random() * 0.4
            },
            aspectWords: aspectWords
          };
        }

        this.isAnalyzing = false;
      }, 1500);
    }
  }
}
</script>

<style>
/* 重置样式，确保页面贴紧浏览器边缘 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body, html {
  margin: 0;
  padding: 0;
  height: 100%;
  overflow: hidden;
}

.sentiment-app {
  display: flex;
  height: 100vh;
  font-family: Arial, sans-serif;
  overflow: hidden;
}

/* 侧边栏样式 */
.sidebar {
  width: 220px;
  background-color: #f5f7fa;
  border-right: 1px solid #e6e9ef;
  padding: 20px 0;
  height: 100vh; /* 确保侧边栏高度占满视口 */
  overflow-y: auto;
}

.sidebar h2 {
  padding: 0 20px;
  margin-bottom: 20px;
  color: #333;
  font-size: 18px;
}

.mode-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.mode-list li {
  padding: 12px 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.mode-list li:hover {
  background-color: #e6e9ef;
}

.mode-list li.active {
  background-color: #e3f2fd;
  color: #1976d2;
  font-weight: bold;
  border-left: 3px solid #1976d2;
}

/* 内容区域样式 */
.content {
  flex: 1;
  padding: 20px 30px;
  overflow-y: auto;
  height: 100vh; /* 确保内容区高度占满视口 */
}

.content h1 {
  margin-bottom: 30px;
  color: #333;
  font-size: 24px;
}

.analysis-panel {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  padding: 24px;
}

.mode-title {
  margin-bottom: 24px;
  border-bottom: 1px solid #e6e9ef;
  padding-bottom: 16px;
}

.mode-title h2 {
  margin: 0 0 8px;
  color: #333;
  font-size: 20px;
}

.mode-title p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

/* 模型选择区域 */
.model-selection {
  margin-bottom: 24px;
}

.model-selection h3 {
  margin: 0 0 12px;
  font-size: 16px;
}

.model-selection select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.model-description {
  margin-top: 8px;
  color: #666;
  font-size: 13px;
  font-style: italic;
}

/* 输入区域 */
.input-area {
  margin-bottom: 24px;
}

.input-area h3 {
  margin: 0 0 12px;
  font-size: 16px;
}

.input-area textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  resize: vertical;
}

/* 方面选择 */
.aspects-selection {
  margin-top: 16px;
}

.aspects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
  margin-top: 12px;
}

.aspect-checkbox {
  display: flex;
  align-items: center;
  font-size: 14px;
}

.aspect-checkbox input {
  margin-right: 6px;
}

/* 按钮 */
.action-buttons {
  margin-top: 20px;
  display: flex;
  gap: 12px;
}

.analyze-btn {
  padding: 10px 24px;
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s;
  width: 100%;
}

.analyze-btn:hover {
  background-color: #1565c0;
}

.analyze-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* 新的三框结果展示区域 */
.three-box-result {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 16px;
  margin-top: 24px;
}

.result-box {
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  overflow: hidden;
}

.result-box h3 {
  background-color: #f5f7fa;
  padding: 12px 16px;
  margin: 0;
  font-size: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.box-content {
  padding: 16px;
  min-height: 150px;
  max-height: 200px;
  overflow-y: auto;
}

.aspect-word {
  display: inline-block;
  background-color: #e3f2fd;
  padding: 4px 10px;
  border-radius: 16px;
  margin: 4px;
  font-size: 14px;
}

.polarity-item {
  padding: 8px 12px;
  margin-bottom: 8px;
  border-radius: 4px;
}

.polarity-item.positive {
  background-color: rgba(76, 175, 80, 0.1);
  border-left: 3px solid #4caf50;
}

.polarity-item.neutral {
  background-color: rgba(255, 152, 0, 0.1);
  border-left: 3px solid #ff9800;
}

.polarity-item.negative {
  background-color: rgba(244, 67, 54, 0.1);
  border-left: 3px solid #f44336;
}

/* 原有结果区域样式 */
.result-area {
  margin-top: 30px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.result-area h3 {
  margin: 0 0 16px;
  font-size: 16px;
}

/* 多方面分析结果 */
.aspect-results {
  display: grid;
  gap: 16px;
}

.aspect-item {
  display: grid;
  grid-template-columns: 100px 80px 1fr;
  align-items: center;
  gap: 12px;
}

.aspect-name {
  font-weight: bold;
}

.aspect-score {
  text-align: center;
}

.score-bar {
  height: 10px;
  background-color: #e0e0e0;
  border-radius: 5px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: linear-gradient(to right, #f44336, #ffeb3b, #4caf50);
  border-radius: 5px;
  transition: width 0.5s;
}

/* 情绪分析结果 */
.emotion-chart {
  display: grid;
  gap: 12px;
}

.emotion-bar {
  display: grid;
  grid-template-columns: 60px 1fr 50px;
  align-items: center;
  gap: 10px;
}

.emotion-label {
  font-weight: bold;
  font-size: 14px;
}

.emotion-value-bar {
  height: 20px;
  background-color: #2196f3;
  border-radius: 4px;
}

.emotion-value {
  font-size: 14px;
  text-align: right;
}

/* 确保色彩一致 */
.positive {
  color: #4caf50;
}

.neutral {
  color: #ff9800;
}

.negative {
  color: #f44336;
}
</style>