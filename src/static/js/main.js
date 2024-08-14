$(async function(){
  async function readTemplate(name) {
    let resp = await fetch(`/static/templates/${name}?t=${CURRENT_REQUEST_ID}`)
    return resp.text();
  }
  async function LoadComponent(name) {
    let jsContent = await readTemplate(name + '.js');
    let htmlContent = await readTemplate(name + '.html');
    let component = eval('(' + jsContent + ')');
    component.template = htmlContent;
    return component;
  }

  const components = {
    MainLayout: await LoadComponent('MainLayout'),
    HomePage: await LoadComponent('HomePage'),
    Viewer: await LoadComponent('Viewer'),
    ViewerItem: await LoadComponent('ViewerItem'),
    Plus: ElementPlusIconsVue.Plus,
    ArrowRight: ElementPlusIconsVue.ArrowRight,
    ArrowLeft: ElementPlusIconsVue.ArrowLeft,
  }
  _.each(components, (item) => {
    // 根据名字查找对应的组件
    item.components = _.reduce(item.components, (ret, name) => {
      ret[name] = components[name];
      return ret;
    }, {})
  });


  var router = new VueRouter.createRouter({
    history: VueRouter.createWebHashHistory(),
    routes: [
      {
        path: '/',
        component: components.MainLayout,
        children: [
          {
            path: '',
            component: components.HomePage,
            name: 'Home',
          },
        ],
      }
    ],
    route404: {
      path: '/404',
      component: {
        template: '<div>not found</div>'
      }
    },
  });

  window.app = Vue.createApp({});
  app.use(ElementPlus);
  app.use(router);

  app.mount('#app');
});
