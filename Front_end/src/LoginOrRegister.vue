<template>
  <div class="login-container">
    <!-- 左侧宣传区域 -->
    <div class="left-section">
      <h1 class="left-title">指针平台助力学校构建</h1>
      <h2 class="left-subtitle">新一代智慧校园</h2>
      <div class="left-decoration">
        <div class="decoration-icons">
          <div class="icon-card"></div>
          <div class="icon-chart"></div>
          <div class="icon-book"></div>
          <div class="icon-users"></div>
          <div class="icon-laptop"></div>
          <div class="icon-file"></div>
        </div>
      </div>
      <p class="left-footer">引擎 • 全终端 • 数据驱动</p>
    </div>
    
    <!-- 右侧登录区域 -->
    <div class="right-section">
      <div class="form-container">
        <h3 class="form-title">指针平台</h3>
        
        <!-- 登录方式切换 -->
        <div class="login-tabs">
          <button 
            class="tab-btn" 
            :class="{ active: loginMethod === 'account' }"
            @click="loginMethod = 'account'"
          >
            账号登录
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: loginMethod === 'scan' }"
            @click="loginMethod = 'scan'"
          >
            扫码登录
          </button>
        </div>
        
        <!-- 账号登录表单 -->
        <form v-if="loginMethod === 'account'" class="form" @submit.prevent="handleSubmit">
          <div class="input-group">
            <label class="input-label">用户名</label>
            <div class="input-wrapper">
              <span class="input-icon">👤</span>
              <input
                v-model.trim="formData.phone"
                type="tel"
                class="input"
                placeholder="请输入手机号"
                required
                @input="filterPhone"
              />
            </div>
            <span v-if="phoneError" class="error-text">{{ phoneError }}</span>
          </div>

          <!-- 登录模式：显示密码输入框 -->
          <div v-if="isLoginForm" class="input-group">
            <label class="input-label">密码</label>
            <div class="input-wrapper">
              <span class="input-icon">🔒</span>
              <input
                v-model="formData.password"
                :type="showPassword ? 'text' : 'password'"
                class="input password-input"
                placeholder="请输入密码"
                required
              />
              <button
                type="button"
                class="eye-button"
                @click="togglePasswordVisibility"
                aria-label="切换密码可见性"
              >
                <svg v-if="!showPassword" class="eye-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
                <svg v-else class="eye-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                  <line x1="1" y1="1" x2="23" y2="23"></line>
                </svg>
              </button>
            </div>
            <span v-if="passwordError" class="error-text">{{ passwordError }}</span>
          </div>

          <!-- 注册模式：显示验证码输入框 -->
          <div v-else class="input-group">
            <label class="input-label">验证码</label>
            <div class="input-wrapper code-wrapper">
              <span class="input-icon">🔢</span>
              <input
                v-model.trim="formData.code"
                type="text"
                class="input"
                placeholder="请输入验证码"
                maxlength="6"
              />
              <button
                type="button"
                class="send-code-btn"
                :disabled="countdown > 0 || !validatephone(formData.phone)"
                @click="sendCode"
              >
                {{ countdown > 0 ? `${countdown}s后重试` : '获取验证码' }}
              </button>
            </div>
            <span v-if="codeError" class="error-text">{{ codeError }}</span>
          </div>

          <div class="form-actions">
            <button class="form-btn" type="submit" :disabled="isSubmitting">
              <span v-if="isSubmitting" class="spinner"></span>
              <span v-else>{{ isLoginForm ? '登录' : '注册' }}</span>
            </button>
          </div>

          <div v-if="submitMessage" class="submit-message" :class="submitMessage.type">
            {{ submitMessage.text }}
          </div>
        </form>
        
        <!-- 扫码登录表单 -->
        <div v-else class="scan-login">
          <div class="qrcode-container">
            <div class="qrcode-placeholder">
              <p>请使用指针平台APP扫码登录</p>
            </div>
          </div>
        </div>
        
        <!-- 注册链接 -->
        <div class="register-link">
          <span>{{ isLoginForm ? '还没有账号？' : '已有账号？' }}</span>
          <button class="register-btn" @click="toggleFormMode">{{ isLoginForm ? '立即注册' : '返回登录' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import request from './utils/request';

export default {
  name: 'LoginOrRegister',
  emits: ['login-success'],

  data() {
    return {
      isLoginForm: true,
      loginMethod: 'account', // account 或 scan
      showPassword: false,
      isSubmitting: false,

      // 表单数据
      formData: {
        phone: '',
        password: '',
        code: '' // 新增验证码字段
      },

      // 验证码相关状态
      countdown: 0,
      timer: null,
      isCodeSent: false,

      // 错误提示
      phoneError: '',
      passwordError: '',
      codeError: '',
      submitMessage: null
    }
  },

  // 组件卸载时清除定时器，防止内存泄漏
  beforeUnmount() {
    if (this.timer) clearInterval(this.timer);
  },

  methods: {
    filterPhone(e) {
      this.formData.phone = e.target.value.replace(/[^\d]/g, '');
    },

    // 发送验证码逻辑
    sendCode() {
      // 1. 校验手机号
      if (!this.validatephone(this.formData.phone)) {
        this.phoneError = '请输入正确的11位手机号';
        return;
      }
      this.phoneError = '';

      // 2. 模拟发送请求
      // 在实际项目中，这里应该调用 await request.post('/send-code', ...)
      console.log(`模拟发送验证码到: ${this.formData.phone}`);

      // 3. 提示用户
      this.submitMessage = {
        type: 'success', // 使用绿色提示
        text: '验证码已发送，请注意查收'
      };

      // 4. 开始倒计时
      this.isCodeSent = true;
      this.countdown = 60;
      this.timer = setInterval(() => {
        this.countdown--;
        if (this.countdown <= 0) {
          clearInterval(this.timer);
          this.timer = null;
        }
      }, 1000);
    },

    async handleSubmit() {
      this.resetErrors();

      // 通用验证
      let isValid = true;
      if (!this.validatephone(this.formData.phone)) {
        this.phoneError = '请输入正确的11位手机号';
        isValid = false;
      }

      if (this.isLoginForm) {
        // 登录模式验证密码
        const passwordValidation = this.validatePassword(this.formData.password);
        if (passwordValidation) {
          this.passwordError = passwordValidation;
          isValid = false;
        }
      } else {
        // 注册模式验证验证码
        if (!this.formData.code || this.formData.code.length < 4) {
          this.codeError = '请输入正确的验证码';
          isValid = false;
        }
      }

      if (!isValid) return;

      this.isSubmitting = true;

      try {
        if (this.isLoginForm) {
          // --- 登录逻辑 (保持不变) ---
          const response = await request.post('/login', {
            username: this.formData.phone,
            password: this.formData.password
          });

          localStorage.setItem('token', response.access_token);
          localStorage.setItem('userPhone', this.formData.phone);
          localStorage.setItem('userType', response.user_type);
          localStorage.setItem('userId', response.user_id);

          this.submitMessage = {
            type: 'success',
            text: '登录成功，正在跳转...'
          };

          setTimeout(() => {
            console.log('Login success, user_type:', response.user_type);
            this.$emit('login-success', {
              token: response.access_token,
              userType: response.user_type,
              phone: this.formData.phone
            });
          }, 800);

        } else {
          // --- 注册逻辑 (新) ---

          // 注意：因为后端目前强制需要密码，而我们在注册页隐藏了密码框
          // 这里我们为了演示流程，默认设置一个初始密码（如 123456）
          // 实际项目中，你应该让后端支持验证码登录，或者在验证码通过后让用户设置密码
          const defaultPassword = "123456";

          await request.post('/register', {
            user_phone: this.formData.phone,
            password: defaultPassword
          });

          this.submitMessage = {
            type: 'success',
            text: `注册成功！默认密码为 ${defaultPassword}，请登录`
          };

          setTimeout(() => {
            this.toggleFormMode(); // 切换回登录页
          }, 2000);
        }
      } catch (error) {
        console.error(error);
        this.submitMessage = {
          type: 'error',
          text: error.response?.data?.detail || '操作失败，请重试'
        };
      } finally {
        this.isSubmitting = false;
      }
    },

    toggleFormMode() {
      this.isLoginForm = !this.isLoginForm;
      this.loginMethod = 'account'; // 切换模式时默认使用账号登录
      this.resetForm();
      this.resetErrors();

      // 切换模式时重置倒计时
      if (this.timer) {
        clearInterval(this.timer);
        this.timer = null;
      }
      this.countdown = 0;
    },

    togglePasswordVisibility() {
      this.showPassword = !this.showPassword;
    },

    validatephone(phone) {
      const re = /^1[3-9]\d{9}$/;
      return re.test(phone);
    },

    validatePassword(password) {
      if (!password || password.length < 6) {
        return '密码必须至少6个字符';
      }
      return '';
    },

    resetForm() {
      this.formData = {
        name: '',
        phone: '',
        password: '',
        code: ''
      };
    },

    resetErrors() {
      this.phoneError = '';
      this.passwordError = '';
      this.codeError = '';
      this.submitMessage = null;
    },

    handleForgotPassword() {
      if (!this.formData.phone) {
        this.phoneError = '请输入手机号';
        return;
      }
      this.submitMessage = {
        type: 'info',
        text: '密码重置功能开发中...'
      };
    }
  },
  watch: {
    'formData.phone'(newVal) {
      if (newVal && this.validatephone(newVal)) {
        this.phoneError = '';
      }
    },
    'formData.password'(newVal) {
      if (newVal && newVal.length >= 6) {
        this.passwordError = '';
      }
    },
    'formData.code'(newVal) {
      if (newVal && newVal.length >= 4) {
        this.codeError = '';
      }
    }
  }
}
</script>

<style scoped>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.login-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background: #f8f9fa;
}

/* 左侧宣传区域 */
.left-section {
  flex: 1;
  background: #f0f8ff;
  padding: 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.left-title {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin-bottom: 10px;
  line-height: 1.2;
}

.left-subtitle {
  font-size: 24px;
  font-weight: 600;
  color: #1890ff;
  margin-bottom: 60px;
}

.left-decoration {
  position: relative;
  height: 300px;
  margin: 40px 0;
}

.decoration-icons {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 300px;
  height: 300px;
  position: relative;
}

.decoration-icons > div {
  position: absolute;
  width: 60px;
  height: 60px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.icon-card {
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  background: #e6f7ff !important;
}

.icon-chart {
  top: 40px;
  right: 20px;
  background: #f6ffed !important;
}

.icon-book {
  bottom: 40px;
  right: 20px;
  background: #fff7e6 !important;
}

.icon-users {
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  background: #fff1f0 !important;
}

.icon-laptop {
  bottom: 40px;
  left: 20px;
  background: #f9f0ff !important;
}

.icon-file {
  top: 40px;
  left: 20px;
  background: #e8f5ff !important;
}

.left-footer {
  font-size: 14px;
  color: #999;
  margin-top: 60px;
}

/* 右侧登录区域 */
.right-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.form-container {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.form-title {
  font-size: 24px;
  font-weight: 700;
  color: #333;
  margin-bottom: 30px;
  text-align: center;
}

/* 登录方式切换 */
.login-tabs {
  display: flex;
  margin-bottom: 30px;
  border-bottom: 1px solid #e8e8e8;
}

.tab-btn {
  flex: 1;
  padding: 10px 0;
  background: none;
  border: none;
  font-size: 16px;
  font-weight: 500;
  color: #999;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.tab-btn.active {
  color: #1890ff;
  font-weight: 600;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: #1890ff;
}

/* 表单样式 */
.form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  transition: border-color 0.3s;
}

.input-wrapper:focus-within {
  border-color: #1890ff;
}

.input-icon {
  padding: 0 12px;
  color: #999;
  font-size: 16px;
}

.input {
  flex: 1;
  border: none;
  outline: none;
  padding: 12px 0;
  font-size: 14px;
  color: #333;
}

.password-input {
  padding-right: 40px;
}

.code-wrapper {
  padding-right: 8px;
}

.send-code-btn {
  position: absolute;
  right: 8px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.3s;
}

.send-code-btn:hover:not(:disabled) {
  background: #40a9ff;
}

.send-code-btn:disabled {
  background: #d9d9d9;
  cursor: not-allowed;
}

.eye-button {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
  display: flex;
  align-items: center;
  color: #999;
}

.eye-icon {
  width: 20px;
  height: 20px;
}

.form-actions {
  margin-top: 10px;
}

.form-btn {
  width: 100%;
  padding: 14px;
  border-radius: 8px;
  border: none;
  background: #1890ff;
  color: white;
  cursor: pointer;
  font-weight: 600;
  font-size: 16px;
  transition: all 0.3s;
  display: flex;
  justify-content: center;
  align-items: center;
}

.form-btn:hover:not(:disabled) {
  background: #40a9ff;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
}

.form-btn:disabled {
  background: #d9d9d9;
  cursor: not-allowed;
}

/* 扫码登录样式 */
.scan-login {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.qrcode-container {
  width: 200px;
  height: 200px;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
}

.qrcode-placeholder {
  text-align: center;
  color: #999;
  font-size: 14px;
}

/* 注册链接 */
.register-link {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #666;
}

.register-btn {
  background: none;
  border: none;
  color: #1890ff;
  cursor: pointer;
  font-weight: 600;
  padding: 0 5px;
  margin-left: 5px;
}

/* 错误提示 */
.error-text {
  color: #f5222d;
  font-size: 12px;
  padding-left: 5px;
}

/* 提交消息 */
.submit-message {
  padding: 10px;
  border-radius: 8px;
  font-size: 12px;
  text-align: center;
  margin-top: 10px;
}

.submit-message.success {
  background-color: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.submit-message.error {
  background-color: #fff1f0;
  color: #f5222d;
  border: 1px solid #ffccc7;
}

.submit-message.info {
  background-color: #e6f7ff;
  color: #1890ff;
  border: 1px solid #91d5ff;
}

/* 加载动画 */
.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
  }
  
  .left-section {
    flex: none;
    height: 300px;
    padding: 20px;
  }
  
  .left-title {
    font-size: 24px;
  }
  
  .left-subtitle {
    font-size: 18px;
    margin-bottom: 30px;
  }
  
  .decoration-icons {
    width: 200px;
    height: 200px;
  }
  
  .decoration-icons > div {
    width: 40px;
    height: 40px;
    font-size: 16px;
  }
  
  .right-section {
    flex: 1;
    padding: 20px;
  }
  
  .form-container {
    padding: 30px;
  }
}
</style>