const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 8080
  },
  pages: {
    index: {
      entry: 'src/main.js',
      title: 'Robot.io',
    }
  }
})
