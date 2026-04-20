<script setup>
import { ref, onMounted } from 'vue';
import StudentPage from './StudentPage.vue';
import TeacherPage from './TeacherPage.vue';
import LoginOrRegister from './LoginOrRegister.vue';

const isLoggedIn = ref(localStorage.getItem('token') !== null);
const userType = ref(localStorage.getItem('userType') || 'student');

console.log('Initial userType:', userType.value);
console.log('Initial localStorage userType:', localStorage.getItem('userType'));

const handleLoginSuccess = (userInfo) => {
  console.log('Login success received:', userInfo);
  isLoggedIn.value = true;
  userType.value = userInfo.userType;
  localStorage.setItem('token', userInfo.token);
  localStorage.setItem('userType', userInfo.userType);
  localStorage.setItem('phone', userInfo.phone);
  console.log('Updated userType:', userType.value);
  console.log('Updated localStorage userType:', localStorage.getItem('userType'));
};

const handleLogout = () => {
  isLoggedIn.value = false;
  userType.value = 'student';
  localStorage.removeItem('token');
  localStorage.removeItem('userType');
  localStorage.removeItem('phone');
  console.log('Logged out, userType reset to:', userType.value);
};
</script>

<template>
  <div class="app-container">
    <!-- 登录/注册页面 -->
    <LoginOrRegister v-if="!isLoggedIn" @login-success="handleLoginSuccess" />
    
    <!-- 学生端页面 -->
    <StudentPage v-else-if="userType === 'student'" @logout="handleLogout" />
    
    <!-- 教师端页面 -->
    <TeacherPage v-else-if="userType === 'teacher'" @logout="handleLogout" />
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f5f5f5;
}

.app-container {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}
</style>