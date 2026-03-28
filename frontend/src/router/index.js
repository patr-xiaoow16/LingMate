import { createRouter, createWebHistory } from "vue-router";
import HomePage from "../views/HomePage.vue";
import AnalysisPage from "../views/AnalysisPage.vue";
import WorkspacePage from "../views/WorkspacePage.vue";
import ReviewPage from "../views/ReviewPage.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomePage,
      meta: { nav: "home" },
    },
    {
      path: "/analysis/:lessonId",
      name: "analysis",
      component: AnalysisPage,
      meta: { nav: "analysis" },
    },
    {
      path: "/workspace/:lessonId/:moduleKey?",
      name: "workspace",
      component: WorkspacePage,
      meta: { nav: "workspace" },
    },
    {
      path: "/review/:lessonId?",
      name: "review",
      component: ReviewPage,
      meta: { nav: "review" },
    },
  ],
});

export default router;
