import { defineConfig } from "vitepress";

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "Tianditu Tools",
  description: "QGIS Plugin",
  head: [["link", { rel: "icon", href: "/favicon.ico" }]],
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    logo: "/logo.svg",
    nav: [
      { text: "主页", link: "/" },
      // { text: "开发笔记", link: "https://liuxs.pro" },
    ],

    sidebar: [
      {
        text: "使用说明",
        items: [{ text: "简介", link: "/intro" }],
      },
    ],

    socialLinks: [{ icon: "github", link: "https://github.com/liuxsdev/qgis-plugin-tianditu" }],
  },
});
