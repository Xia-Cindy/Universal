<template>
  <main class="auth-page">
    <section class="auth-panel">
      <p class="eyebrow">Universe OS</p>
      <h1>创建你的 Universe</h1>
      <p class="surface-copy">使用邮箱验证码完成注册，之后你的 Goals、Knowledge 和学习记录都会归属于自己的账户。</p>
      <form v-if="!verificationRequested" @submit.prevent="requestCode">
        <label>显示名称<input v-model="form.displayName" required placeholder="你的名字" /></label>
        <label>邮箱<input v-model="form.email" required type="email" placeholder="you@example.com" /></label>
        <label>密码<input v-model="form.password" required minlength="8" type="password" placeholder="至少 8 位" /></label>
        <button type="submit" :disabled="isBusy">发送验证码</button>
      </form>
      <form v-else @submit.prevent="verifyCode">
        <p class="status-pill">验证码已发送至 {{ form.email }}</p>
        <label>验证码<input v-model="code" required inputmode="numeric" maxlength="6" placeholder="6 位验证码" /></label>
        <button type="submit" :disabled="isBusy">完成注册</button>
        <button class="secondary-action" type="button" @click="verificationRequested = false">修改邮箱</button>
      </form>
      <p v-if="status" class="surface-copy">{{ status }}</p>
      <RouterLink class="secondary-action" to="/">返回 Universe Home</RouterLink>
    </section>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { requestRegistration, verifyRegistration } from '../services/api'

const router = useRouter()
const form = ref({ displayName: '', email: '', password: '' })
const code = ref('')
const status = ref('')
const isBusy = ref(false)
const verificationRequested = ref(false)

async function requestCode() {
  isBusy.value = true
  try {
    await requestRegistration(form.value)
    verificationRequested.value = true
    status.value = '请查收邮箱中的验证码。'
  } catch (error) {
    status.value = error instanceof Error ? error.message : '验证码发送失败。'
  } finally {
    isBusy.value = false
  }
}

async function verifyCode() {
  isBusy.value = true
  try {
    await verifyRegistration({ email: form.value.email, code: code.value })
    await router.push('/study')
  } catch (error) {
    status.value = error instanceof Error ? error.message : '验证码校验失败。'
  } finally {
    isBusy.value = false
  }
}
</script>
