const app = Vue.createApp({
  el: '#app',
  data () {
    return {
      DS: [ 'fma', 'musicnet' , 'vctk', 'yang' ],
      CR: {
        fma: 1024,
        musicnet: 1024,
        vctk: 1024,
        yang: 1024
      },
      rate: [ '0.5', '0.75', '1.0', '1.5', '1.25', '1.75', '2.0' ]
    }
  },
  watch: {
    'CR.fma': function () {
      for (const r of this.rate) {
        this.$refs['fma' + r].load()
      }
    },
    'CR.musicnet': function () {
      for (const r of this.rate) {
        this.$refs['musicnet' + r].load()
      }
    },
    'CR.vctk': function () {
      for (const r of this.rate) {
        this.$refs['vctk' + r].load()
      }
    },
    'CR.yang': function () {
      for (const r of this.rate) {
        this.$refs['yang' + r].load()
      }
    }
  }
})

app.mount('#app')
