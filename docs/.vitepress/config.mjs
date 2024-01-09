import { defineConfig } from "vitepress";

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "Tianditu Tools",
  description: "QGIS Plugin",
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: "指南", link: "/" },
      { text: "开发笔记", link: "/notes" },
    ],

    sidebar: [
      {
        text: "",
        items: [{ text: "使用说明", link: "/intro" }],
      },
      {
        text: "",
        items: [{ text: "开发笔记", link: "/intro" }],
      },
    ],

    socialLinks: [{ icon: "github", link: "https://github.com/liuxsdev/qgis-plugin-tianditu" }],
  },
});
