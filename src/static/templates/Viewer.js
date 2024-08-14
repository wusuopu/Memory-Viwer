{
  name: "Viewer",
  components: ['Plus', 'ViewerItem'],
  props: {
    pid: {
      type: Number
    },
  },
  data() {
    return {
      alias: 'view-1',
      addr: '',
      size: 48,
      content: '',
      items: [],
    }
  },
  methods: {
    addItem() {
      let reg = /^[0-9a-fA-F]+$/
      if (!reg.test(this.addr)) {
        ElementPlus.ElMessage.error('地址无效')
        return
      }
      this.items = _.concat(this.items, [{alias: this.alias, addr: this.addr, size: this.size}])
      this.alias = `view-${this.items.length + 1}`
      this.addr = ''
      this.size = 48
    },
    handleDelete(item, index) {
      this.items = _.filter(this.items, (o, idx) => idx !== index)
    },
  },
}
