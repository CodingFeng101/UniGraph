<template>
  <div class="auth-field" :class="{ 'auth-field--compact': compact }">
    <label class="auth-field__label" :for="inputId">{{ label }}</label>
    <div class="auth-field__control">
      <span class="auth-field__icon" aria-hidden="true">
        <i :data-lucide="icon"></i>
      </span>
      <input
        :id="inputId"
        class="auth-field__input"
        :class="{ 'auth-field__input--suffix': $slots.suffix }"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :maxlength="maxlength"
        :autocomplete="autocomplete"
        @input="handleInput"
      />
      <span v-if="$slots.suffix" class="auth-field__suffix">
        <slot name="suffix" />
      </span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AuthField',
  props: {
    modelValue: { type: String, default: '' },
    inputId: { type: String, required: true },
    label: { type: String, required: true },
    icon: { type: String, required: true },
    type: { type: String, default: 'text' },
    placeholder: { type: String, default: '' },
    maxlength: { type: [Number, String], default: undefined },
    autocomplete: { type: String, default: 'off' },
    compact: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
  methods: {
    handleInput(event) {
      this.$emit('update:modelValue', event.target.value);
    },
  },
  mounted() {
    window.lucide?.createIcons();
  },
};
</script>

<style scoped>
.auth-field {
  margin-bottom: 24px;
}

.auth-field--compact {
  margin-bottom: 14px;
}

.auth-field__label {
  display: block;
  margin-bottom: 8px;
  color: var(--claude-muted-foreground);
  font-family: var(--claude-font-sans);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.auth-field--compact .auth-field__label {
  margin-bottom: 6px;
}

.auth-field__control {
  position: relative;
}

.auth-field__icon {
  position: absolute;
  left: 16px;
  top: 50%;
  z-index: 1;
  display: flex;
  color: var(--claude-muted-foreground);
  pointer-events: none;
  transform: translateY(-50%);
}

.auth-field__icon :deep(svg) {
  width: 18px;
  height: 18px;
  stroke-width: 1.8;
}

.auth-field__input {
  width: 100%;
  height: 48px;
  padding: 0 16px 0 48px;
  border: 1px solid var(--claude-input);
  border-radius: 14px;
  outline: none;
  background: var(--claude-card);
  color: var(--claude-foreground);
  font-family: var(--claude-font-sans);
  font-size: 14px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.auth-field__input--suffix {
  padding-right: 130px;
}

.auth-field__input:focus {
  border-color: var(--claude-brand-500);
  box-shadow: 0 0 0 3px rgba(201, 100, 66, 0.12);
}

.auth-field__suffix {
  position: absolute;
  right: 10px;
  top: 50%;
  display: flex;
  align-items: center;
  transform: translateY(-50%);
}
</style>
