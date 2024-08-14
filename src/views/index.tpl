<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>内存查看器</title>
% if DEBUG:
  <link rel="stylesheet" href="/static/vendor/css/element-plus.css">
  <link rel="stylesheet" href="/static/css/main.css?{{roundKey}}">

  <script src="/static/vendor/js/jquery-3.7.1.js"></script>
  <script src="/static/vendor/js/vue.global.js"></script>
  <script src="/static/vendor/js/vuex.global.js"></script>
  <script src="/static/vendor/js/vue-router.global.js"></script>
  <script src="/static/vendor/js/lodash-4.17.21.js"></script>
  <script src="/static/vendor/js/tailwindcss-3.4.5.js"></script>
  <script src="/static/vendor/js/element-plus.js"></script>
  <script src="/static/vendor/js/element-plus-icons.js"></script>

  <script src="/static/js/main.js?{{roundKey}}"></script>
% else:
  <link rel="stylesheet" href="/static/css/bundle.css?{{roundKey}}">
  <script src="/static/js/bundle.js?{{roundKey}}"></script>
% end
</head>
<body>
  <script>
    window.CURRENT_VERSION = '{{ VERSION }}';
    window.CURRENT_REQUEST_ID = '{{ roundKey }}';
  </script>
  <div id="app" class="mx-[auto] p-4 max-w-[1300px] min-w-[1100px]">
    <router-view />
  </div>
</body>
</html>
