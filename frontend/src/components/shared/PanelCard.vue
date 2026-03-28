<script setup>
const props = defineProps({
  title: {
    type: String,
    default: "",
  },
  eyebrow: {
    type: String,
    default: "",
  },
  tone: {
    type: String,
    default: "neutral",
  },
});
</script>

<template>
  <section class="surface" :class="`surface-${props.tone}`">
    <div v-if="props.eyebrow || props.title" class="panel-head">
      <p v-if="props.eyebrow" class="eyebrow">{{ props.eyebrow }}</p>
      <h3 v-if="props.title" class="panel-title">{{ props.title }}</h3>
    </div>
    <slot />
  </section>
</template>
