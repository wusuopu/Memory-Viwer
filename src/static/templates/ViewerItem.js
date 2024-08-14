{
  name: "ViewerItem",
  components: [],
  props: {
    pid: {
      type: Number
    },
    alias: {
      type: String
    },
    addr: {
      type: String
    },
    size: {
      type: Number
    },
  },
  data() {
    return {
      content: [],
      duplicateContent: [],
      error: '',
    }
  },
  methods: {
    async readData() {
      try {
        let resp = await fetch(
          "/api/v1/memory", {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({pid: this.pid, address: this.addr, size: this.size})
          }
        )
        let ret = await resp.json()
        return ret.data
      } catch (error) {
        ElementPlus.ElMessage.error('读取内存失败')
        this.error = error
        return []
      }
    },
    async refresh() {
      this.content = await this.readData()
    },
    async refreshDuplicate() {
      this.duplicateContent = await this.readData()
    },
    remove() {
      this.$emit('delete')
    },
    toHex(value) {
      return _.padStart(value.toString(16), 2, '0').toUpperCase()
    },
    getChunkValue(row, col) {
      let v = this.content[row * 0x10 + col]
      if (_.isUndefined(v)) { return '??' }
      return this.toHex(v)
    },
    getChunkValue2(row, col) {
      let v = this.duplicateContent[row * 0x10 + col]
      if (_.isUndefined(v)) { return '??' }
      return this.toHex(v)
    },
    compareClassName(row, col, ignore) {
      if (!this.duplicateContent.length) { return '' }

      let v1 = this.content[row * 0x10 + col]
      let v2 = this.duplicateContent[row * 0x10 + col]
      if (v1 !== v2) { return 'text-red-500' }

      if (ignore) { return '' }
      return 'text-green-500'
    },
    copyText(text) {
      console.log('copy text:', text)
      const textArea = document.createElement("textArea");
      textArea.value = text;
      textArea.style.width = 0;
      textArea.style.position = "fixed";
      textArea.style.left = "-999px";
      textArea.style.top = "10px";
      textArea.setAttribute("readonly", "readonly");
      document.body.appendChild(textArea);

      textArea.select();
      let ret = document.execCommand("copy");
      console.log(ret ? 'copy success' : 'copy fail')
      document.body.removeChild(textArea);
      return ret
    },
    copyView(content) {
      let data = _.map(_.chunk(content, 16), (item, row) => {
        return this.addrRows[row] + ' ' + item.join(' ')
      }).join('\n')
      this.copyText(data)
    },
    copyData(content) {
      let data = _.map(_.chunk(content, 16), (item) => {
        return item.join(' ')
      }).join('\n')
      this.copyText(data)
    },
    copyBaseView() {
      this.copyView(this.content)
    },
    copyBaseData() {
      this.copyData(this.content)
    },
    copyDuplicateView() {
      this.copyView(this.duplicateContent)
    },
    copyDuplicateData() {
      this.copyData(this.duplicateContent)
    },
  },
  computed: {
    addrRows() {
      let rows = Math.ceil(this.size / 16)
      let i = 0

      let ret = []
      let baseAddr = parseInt(this.addr, 16)
      while (i < rows) {
        let value = (baseAddr + (i * 0x10)).toString(16)

        let pad
        if (value.length <= 8) {
          pad = 8
        } else {
          pad = 16
        }
        ret.push(_.padStart(value, pad, '0').toUpperCase())

        i++
      }
      return ret
    }
  },
  async mounted() {
    // this.content = await this.readData()
  },
}
