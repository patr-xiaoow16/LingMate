<script setup>
import { computed } from "vue";
import ModuleImmersive from "./ModuleImmersive.vue";
import ModuleVocabulary from "./ModuleVocabulary.vue";
import ModuleChinglish from "./ModuleChinglish.vue";
import ModuleScene from "./ModuleScene.vue";
import ModuleDecoder from "./ModuleDecoder.vue";
import ModuleTone from "./ModuleTone.vue";
import ModulePattern from "./ModulePattern.vue";
import ModuleOutput from "./ModuleOutput.vue";

const props = defineProps({
  module: {
    type: Object,
    required: true,
  },
});

const componentMap = {
  "immersive-listening": ModuleImmersive,
  "vocabulary-deep-dive": ModuleVocabulary,
  "native-vs-chinglish": ModuleChinglish,
  "scene-mapping": ModuleScene,
  "listening-decoder": ModuleDecoder,
  "subtext-and-tone": ModuleTone,
  "pattern-extraction": ModulePattern,
  "output-challenge": ModuleOutput,
};

const activeComponent = computed(() => componentMap[props.module.key] || ModuleImmersive);
</script>

<template>
  <component :is="activeComponent" :module="module" />
</template>
