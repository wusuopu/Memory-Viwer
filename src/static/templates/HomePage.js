{
  name: "Homepage",
  components: ['Viewer', 'ArrowRight', 'ArrowLeft'],
  data() {
    return {
      processes: [],
      currentRow: null,
      attached: [],
      currentTabValue: null,
      coding: 'gbk',
      byteData: 'BD F8 B3 CC C4 DA B4 E6 B2 E9 BF B4',
      strData: '进程内存查看',
    }
  },
  async mounted() {
    await this.refresh()
  },
  methods: {
    async refresh() {
      let resp = await fetch('/api/v1/processes')
      let data = await resp.json()
      _.each(data, (item) => {
        item.exe = item.name.split('\\').slice(-1)[0]
      })
      this.processes = data
      this.currentRow = null
    },
    handleCurrentChange(val) {
      this.currentRow = val
    },
    inject() {
      if (_.includes(this.attached, this.currentRow.pid)) {
        return
      }
      this.attached.push(this.currentRow.pid)
      this.currentTabValue = this.currentRow.pid
    },
    handleRemoveTab(name) {
      this.attached = _.without(this.attached, name)
    },
    async convertBytes2Str() {
      let content = this.byteData.trim()
      if (!content) { return }

      try {
        let resp = await fetch(
          "/api/v1/bytes2str", {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({coding: this.coding, data: content})
          }
        )
        let ret = await resp.json()
        this.strData = ret.data
      } catch (error) {
        ElementPlus.ElMessage.error('转换失败')
        this.strData = ''
      }
    },
    async convertStr2Bytes() {
      let content = this.strData.trim()
      if (!content) { return }

      try {
        let resp = await fetch(
          "/api/v1/str2bytes", {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({coding: this.coding, data: content})
          }
        )
        let ret = await resp.json()
        this.byteData = ret.data
      } catch (error) {
        ElementPlus.ElMessage.error('转换失败')
        this.byteData = ''
      }
    },
  },
}
