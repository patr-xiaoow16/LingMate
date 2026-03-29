import { createRouter, createWebHistory } from "vue-router";

import HomePage from "./views/HomePage.vue";
import AnalysisPage from "./views/AnalysisPage.vue";
import WorkspacePage from "./views/WorkspacePage.vue";
import ReviewPage from "./views/ReviewPage.vue";

const routes = [
  { path: "/", name: "home", component: HomePage },
  { path: "/analysis/:lessonId", name: "analysis", component: AnalysisPage, props: true },
  { path: "/workspace/:lessonId", name: "workspace", component: WorkspacePage, props: true },
  { path: "/review/:lessonId", name: "review", component: ReviewPage, props: true },
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
