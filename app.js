const backend = 'http://34.132.148.183:5000'
const app = Vue.createApp({
  el: '#app',
  data () {
    return {
      live: {
        enable: false,
        source: 'File',
        rate: 0.75
      },
      DS: [ 'fma', 'musicnet' , 'vctk', 'yang' ],
      audio: {
        fma: 0,
        musicnet: 0,
        vctk: 0,
        yang: 0
      },
      CR: {
        fma: 1024,
        musicnet: 1024,
        vctk: 1024,
        yang: 1024
      },
      rate: [ '0.5', '0.75', '1.0', '1.25', '1.5', '1.75', '2.0' ]
    }
  },
  watch: {
    'CR.fma':         function () { this.reload('fma') },
    'audio.fma':      function () { this.reload('fma') },
    'CR.musicnet':    function () { this.reload('musicnet') },
    'audio.musicnet': function () { this.reload('musicnet') },
    'CR.vctk':        function () { this.reload('vctk') },
    'audio.vctk':     function () { this.reload('vctk') },
    'CR.yang':        function () { this.reload('yang') },
    'audio.yang':     function () { this.reload('yang') }
  },
  methods: {
    reload (key) {
      for (const r of this.rate) {
        this.$refs[key + r].load()
      }
    }
  }
})

app.mount('#app')
