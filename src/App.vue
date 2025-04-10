<template>
  <div id="app">
    <SentimentAnalysis />
  </div>
</template>

<script>
import SentimentAnalysis from './components/SentimentAnalysis.vue'

export default {
  name: 'App',
  components: {
    SentimentAnalysis
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  height: 100vh;
}

#app {
  height: 100vh;
}
</style>