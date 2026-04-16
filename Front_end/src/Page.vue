<template>
  <!-- ==================== 主应用容器 ==================== -->
  <div class="app-container" :class="{ 'teacher-mode': userType === 'teacher' }" @click="hideContextMenu">

    <button class="sidebar-toggle-btn" :class="{ 'collapsed': isSidebarCollapsed }" @click.stop="toggleSidebar">
      <svg v-if="!isSidebarCollapsed" viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
        <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
      </svg>
      <svg v-else viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
        <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
      </svg>
    </button>

    <!-- ==================== 侧边栏模块 ==================== -->
    <aside class="sidebar" :class="{ 'collapsed': isSidebarCollapsed }">

      <!-- 侧边栏Logo -->
      <div class="sidebar-logo" v-if="!isSidebarCollapsed">
        <div class="logo-icon">🧪</div>
        <h1 class="logo-text">CEEA 评估系统</h1>
      </div>

      <!-- 用户信息区域 -->
      <div class="user-profile-area" @click="isLoggedIn ? showMy() : showProfile = true">
        <div class="user-avatar">
          <span v-if="isLoggedIn">User</span>
          <span v-else>未登录</span>
        </div>
        <div class="user-info" v-if="!isSidebarCollapsed && isLoggedIn">
          <span class="user-phone">{{ maskedPhone }}</span>
          <span class="user-role">{{ userType === 'teacher' ? '教师账号' : '学生账号' }}</span>
        </div>
      </div>

      <!-- 导航菜单 -->
      <div class="nav-menu">
        <div class="nav-header">
          <!-- 新实验评估按钮 -->
          <button class="new-conversation-btn" @click="resetDashboard">
            <span class="icon">+</span>
            <span>新实验评估</span>
          </button>

          <!-- 功能区域导航 -->
          <div class="nav-function-area">
            <button class="nav-item" :class="{ 'active': currentFunction === 'messages' }" @click="selectFunction('messages')">
              <span class="nav-icon">📩</span><span class="nav-text">消息中心</span>
              <span v-if="unreadCount > 0" class="unread-badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
            </button>
            <button class="nav-item" :class="{ 'active': currentFunction === 'exams' }" @click="selectFunction('exams')">
              <span class="nav-icon">📝</span><span class="nav-text">考试系统</span>
            </button>
            <button class="nav-item" :class="{ 'active': currentFunction === 'classes' }" @click="selectFunction('classes')">
              <span class="nav-icon">🏫</span><span class="nav-text">班级管理</span>
            </button>
          </div>

          <div class="nav-divider"></div>
          <div class="nav-section-title">最近记录</div>
        </div>

        <!-- 历史记录列表 -->
        <div class="history-container">
          <div class="history-list">
            <div
              class="history-item"
              v-for="item in historyConversations"
              :key="item.id"
              @click="loadHistory(item.id)"
              @contextmenu.prevent="showContextMenu($event, item)"
              :class="{ 'active': currentConversationId === item.id }"
              :title="item.title"
            >
              <div class="history-content-wrapper">
                <div class="history-title">{{ item.title || '未命名实验' }}</div>
                <div class="history-time">{{ formatTime(item.updated_at) }}</div>
              </div>
            </div>
            <div class="empty-history" v-if="historyConversations.length === 0">
              暂无历史记录
            </div>
          </div>
        </div>
      </div>
    </aside>

    <div
      v-if="contextMenu.visible"
      class="context-menu"
      :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
      @click.stop
    >
      <div class="menu-item" @click="handleRename">✏️ 重命名</div>
      <div class="menu-item delete" @click="handleDelete">🗑️ 删除记录</div>
    </div>

    <!-- ==================== 主内容区域 ==================== -->
    <main class="main-content">

      <!-- 顶部栏 -->
      <div class="top-bar" v-if="!currentFunction && !showMyPage">
        <!-- 欢迎信息 -->
        <div v-if="!reportData" class="greeting">
           👋 下午好，准备开始实验评估了吗？
        </div>

        <!-- 评估结果头部 -->
        <div v-else class="result-header">
           <div class="header-left">
             <h1 class="result-title">{{ reportData.experiment_name || '化学实验分析报告' }}</h1>
             <p class="result-meta"> · AI 智能评估完成 · {{ formatTime(reportData.create_time) }}</p>
           </div>

           <div class="header-right">
             <div class="score-display">
               <div class="score-main">
                 <span class="score-value">{{ reportData.total_score }}</span>
                 <span class="score-unit">分</span>
               </div>
               <div class="score-badge" :class="getScoreRatingClass(reportData.total_score)">
                 {{ getScoreRating(reportData.total_score) }}
               </div>
             </div>
           </div>
        </div>
      </div>

      <!-- ==================== 仪表板区域 ==================== -->
      <div v-if="!currentFunction && !showMyPage" class="dashboard-wrapper">
        <div class="dashboard-body">

          <!-- ==================== 左侧面板 - 视频上传区域 ==================== -->
          <div v-if="!reportData" class="left-panel">

            <!-- 视频上传卡片 -->
            <div class="card video-card">
              <div class="card-header">
                <h3>上传实验视频</h3>
                <span class="status-badge" v-if="isLoading">分析进行中...</span>
              </div>

              <!-- 学生端：单个视频上传 -->
              <div v-if="userType === 'student'" class="video-area" :class="{ 'has-video': !!selectedVideoURL }">
                <div v-if="selectedVideoURL" class="video-with-controls">
                  <video controls :src="selectedVideoURL" class="real-video"></video>
                  <button class="reselect-btn" @click="$refs.videoInput.click()">重新选择视频</button>
                </div>
                <div v-else class="upload-placeholder" @click="$refs.videoInput.click()">
                  <img :src="evaluate1" class="placeholder-img-icon" alt="Upload Icon" />
                  <p class="upload-title">点击或拖拽视频至此处</p>
                  <p class="upload-desc">支持 MP4, AVI 格式，建议时长 3-5 分钟</p>
                </div>
              </div>

              <!-- 教师端：批量视频上传 -->
              <div v-else class="video-area" :class="{ 'has-videos': selectedFiles.length > 0 }">
                <div v-if="selectedFiles.length > 0" class="batch-upload-container">
                  <h4>已选择 {{ selectedFiles.length }} 个视频文件</h4>
                  <ul class="file-list">
                    <li v-for="(file, index) in selectedFiles" :key="index">
                      {{ file.name }}
                      <button class="remove-file-btn" @click="removeFile(index)">×</button>
                    </li>
                  </ul>
                  <button class="reselect-btn" @click="$refs.videoInput.click()">重新选择视频</button>
                </div>
                <div v-else class="upload-placeholder" @click="$refs.videoInput.click()">
                  <img :src="evaluate1" class="placeholder-img-icon" alt="Upload Icon" />
                  <p class="upload-title">点击或拖拽视频至此处</p>
                  <p class="upload-desc">支持批量上传 MP4, AVI 格式，建议时长 3-5 分钟</p>
                </div>
              </div>

              <!-- 表单区域 -->
              <div class="form-area">
                <div class="input-group">
                  <label>实验名称 <span class="required">*</span></label>
                  <input
                    v-model="customExperimentName"
                    type="text"
                    placeholder="请输入实验名称以提升 AI 识别准确率..."
                    class="modern-input"
                    :disabled="isLoading"
                  />
                  <span v-if="experimentNameError" class="error-text">{{ experimentNameError }}</span>
                </div>

                <div class="action-buttons">
                  <input 
                    type="file" 
                    ref="videoInput" 
                    accept="video/*" 
                    :multiple="userType === 'teacher'" 
                    style="display: none" 
                    @change="handleFileChange" 
                  />
                  <button class="btn-primary" @click="handleMainBtnClick" :disabled="isLoading">
                    {{ isLoading ? 'AI 正在分析...' : (userType === 'student' ? (selectedFile ? '开始智能评估' : '选择视频文件') : (selectedFiles.length > 0 ? '开始批量评估' : '选择视频文件')) }}
                  </button>
                  <button class="btn-text" v-if="(userType === 'student' && selectedVideoURL) || (userType === 'teacher' && selectedFiles.length > 0)" @click="resetSelection" :disabled="isLoading">
                    清空重置
                  </button>
                </div>
              </div>
            </div>

          </div>

          <!-- ==================== 左侧面板 - 评估结果区域 ==================== -->
          <div v-if="reportData" class="left-panel">

            <!-- 步骤评估卡片 -->
            <div class="card timeline-card">
              <div class="card-header timeline-header">
                <h4 class="section-title">步骤评估详情</h4>
                <div class="step-count">{{ reportData.steps.length }} 个步骤</div>
              </div>

              <!-- 步骤时间线 -->
              <div class="step-timeline">
                <div v-for="(step, index) in reportData.steps" :key="index" class="timeline-item" :class="step.status">
                  <div class="timeline-marker"></div>
                  <div class="timeline-content">
                    <div class="step-head">
                      <strong>{{ step.name }}</strong>
                      <span class="tag" :class="step.status">
                        {{ step.status === 'success' ? '规范' : (step.status === 'error' ? '错误' : '需改进') }}
                      </span>
                      <span class="step-score">
                        {{ step.score || 0 }}/{{ step.total_score || 0 }} 分
                      </span>
                    </div>
                    <p>{{ step.comment }}</p>
                  </div>
                </div>
              </div>
            </div>

          </div>

          <!-- ==================== 右侧面板 - 评估结果详情 ==================== -->
          <div v-if="reportData" class="right-panel">

            <div class="result-right-stack">

              <!-- 总体评价卡片 -->
              <div class="card summary-card">
                 <h4>📊 总体评价</h4>
                 <p class="summary-text">{{ reportData.summary || '暂无总体评价' }}</p>
              </div>

              <!-- 得失分详情卡片 -->
              <div class="card summary-card score-points-card">
                 <h4>📋 得失分详情</h4>
                 <div v-for="(step, index) in reportData.steps" :key="index" class="step-score-points">
                   <h5>{{ step.name }}</h5>
                   <div v-if="step.score_points && step.score_points.length" class="score-points-list">
                     <div v-for="(point, pIndex) in step.score_points" :key="pIndex" :class="['score-point-item', point.status]">
                       <div class="score-point-header">
                         <span class="status-icon">{{ point.status === 'pass' ? '✓' : '✗' }}</span>
                         <div class="point-info">
                           <div class="point-name">{{ point.point_name || '评分点' }}</div>
                           <div class="point-description">{{ point.point }}</div>
                         </div>
                         <span class="point-score">{{ point.score || 0 }}分</span>
                         <span v-if="point.status === 'fail' && point.deduction" class="deduction">(扣{{ point.deduction }}分)</span>
                       </div>
                       <div v-if="point.status === 'fail' && point.error_explanation" class="error-explanation">
                         {{ point.error_explanation }}
                       </div>
                     </div>
                   </div>
                   <p v-else class="no-points">暂无详细评分点</p>
                 </div>

              </div>


            </div>

          </div>
        </div>
      </div>

      <!-- ==================== 功能页面区域 ==================== -->
      <div v-if="currentFunction" class="function-page">
        <div class="page-header">

          <h2>{{ functionTitles[currentFunction] }}</h2>
        </div>
        
          <!-- ==================== 班级管理页面 ==================== -->
          <div v-if="currentFunction === 'classes'" class="classes-page">
            <!-- 教师端：创建班级按钮和班级列表 -->
            <div v-if="userType === 'teacher'">
              <!-- 班级列表页面 -->
              <div v-if="!isClassDetailPage">
                <div class="classes-header">
                  <div class="classes-actions">
                    <button class="btn-primary" @click="handleCreateClassClick">创建班级</button>
                  </div>
                  <div class="search-container">
                    <input 
                      type="text" 
                      v-model="searchKeyword" 
                      placeholder="搜索班级名称..." 
                      class="search-input"
                      @input="handleSearch"
                    >
                  </div>
                </div>
                
                <div class="classes-content">
                  <div v-if="filteredTeacherClasses.length > 0" class="classes-list">
                    <div v-for="cls in filteredTeacherClasses" :key="cls.id" class="class-item" @click="enterClassDetail(cls.id)">
                      <div class="class-info">
                        <h4>{{ cls.class_name }}</h4>
                        <p>班级号：{{ cls.class_code }}</p>
                        <p v-if="cls.description">{{ cls.description }}</p>
                        <p>创建时间：{{ formatTime(cls.created_at) }}</p>
                      </div>
                      <div class="class-actions">
                        <button class="btn-text" @click.stop="copyClassCode(cls.class_code)">复制班级号</button>
                        <button class="btn-text delete-btn" @click.stop="deleteClass(cls.id)">解散班级</button>
                      </div>
                    </div>
                  </div>
                  <div v-else-if="!isLoading" class="empty-state">
                    <p>您还没有创建任何班级</p>
                  </div>
                </div>
              </div>
              
              <!-- 班级详情页面（学生列表） -->
              <div v-else class="class-detail">
                <div class="class-detail-header">
                  <button class="btn-text" @click="backToClassList">← 返回班级列表</button>
                  <h3>{{ selectedClass?.class_name }} - 学生列表</h3>
                  <div class="class-detail-actions">
                    <button class="btn-primary" @click="showAddStudentModal = true">添加学生</button>
                    <button class="btn-primary" @click="showImportStudentsModal = true">批量导入</button>
                  </div>
                </div>
                <div class="class-detail-content">
                  <div v-if="classMembers.length > 0" class="student-list">
                    <div v-for="member in classMembers" :key="member.student_id" class="student-item">
                      <div class="student-info">
                        <p>{{ member.student_id }}</p>
                        <p>加入时间：{{ formatTime(member.joined_at) }}</p>
                      </div>
                      <div class="student-actions">
                        <button class="btn-text delete-btn" @click="removeStudent(member.student_id)">删除</button>
                      </div>
                    </div>
                  </div>
                  <div v-else-if="!isLoading" class="empty-state">
                    <p>该班级暂无学生</p>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 学生端：加入班级按钮和班级列表 -->
            <div v-else>
              <div class="classes-header">
                <div class="class-join-section">
                  <div class="form-group">
                    <label>班级号</label>
                    <input v-model="joinClassCode" type="text" class="modern-input" placeholder="请输入班级号">
                  </div>
                  <button class="btn-primary" @click="joinClass" :disabled="isLoading || !joinClassCode.trim()">
                    {{ isLoading ? '加入中...' : '加入班级' }}
                  </button>
                </div>
              </div>
              <div class="classes-content">
                <div v-if="studentClasses.length > 0" class="classes-list">
                  <h3>我的班级</h3>
                  <div class="class-list">
                    <div v-for="cls in studentClasses" :key="cls.id" class="class-item">
                      <div class="class-info">
                        <h4>{{ cls.class_name }}</h4>
                        <p>班级号：{{ cls.class_code }}</p>
                        <p>教师：{{ cls.teacher_id }}</p>
                        <p>加入时间：{{ formatTime(cls.joined_at) }}</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else-if="!isLoading" class="empty-state">
                  <p>您还没有加入任何班级</p>
                </div>
              </div>
            </div>
          </div>
          <!-- ==================== 考试系统模块 ==================== -->
          <div v-else-if="currentFunction === 'exams'" class="exams-page">
            <div class="exams-header">
              <div class="tab-buttons">
                <!-- 教师端：显示考试管理和模板标签页 -->
                <template v-if="userType === 'teacher'">
                  <button class="tab-btn" :class="{ 'active': examsTab === 'exams' }" @click="examsTab = 'exams'">考试管理</button>
                  <button class="tab-btn" :class="{ 'active': examsTab === 'templates' }" @click="examsTab = 'templates'">评价表模板</button>
                </template>
                <!-- 学生端：只显示考试标签页，标题改为我的考试 -->
                <template v-else>
                  <h2>我的考试</h2>
                </template>
              </div>
            </div>
            
            <!-- 考试管理标签页 -->
            <div v-if="examsTab === 'exams' || userType === 'student'" class="exams-content">
              <!-- 教师端：显示发布考试按钮 -->
              <div v-if="userType === 'teacher'" class="exams-actions">
                <button class="btn-primary" @click="handleCreateExamClick">发布考试</button>
              </div>
              
              <!-- 教师端：显示教师发布的考试列表 -->
              <div v-if="userType === 'teacher' && teacherExams.length > 0" class="exams-list">
                <div v-for="exam in teacherExams" :key="exam.id" class="exam-item">
                  <div class="exam-info">
                    <h4>{{ exam.exam_name }}</h4>
                    <p>发布时间：{{ formatTime(exam.created_at) }}</p>
                    <p>发布班级：{{ exam.class_name }}</p>
                    <p>状态：{{ exam.status }}</p>
                  </div>
                  <div class="exam-actions">
                    <button class="btn-text" @click="viewExamDetails(exam.id)">查看详情</button>
                    <button class="btn-text delete-btn" @click="deleteExam(exam.id)">删除</button>
                  </div>
                </div>
              </div>
              <div v-else-if="userType === 'teacher' && !isLoading" class="empty-state">
                <p>您还没有发布任何考试</p>
              </div>
              
              <!-- 学生端：显示学生可参加的考试列表 -->
              <div v-if="userType === 'student' && studentExams.length > 0" class="exams-list">
                <div v-for="exam in studentExams" :key="exam.id" class="exam-item">
                  <div class="exam-info">
                    <h4>{{ exam.exam_name }}</h4>
                    <p>发布时间：{{ formatTime(exam.created_at) }}</p>
                    <p>发布班级：{{ exam.class_name }}</p>
                    <p>状态：{{ exam.status }}</p>
                    <p v-if="exam.start_time">开始时间：{{ formatTime(exam.start_time) }}</p>
                    <p v-if="exam.end_time">结束时间：{{ formatTime(exam.end_time) }}</p>
                  </div>
                  <div class="exam-actions">
                    <button class="btn-text" @click="viewExamDetails(exam.id)">查看详情</button>
                    <button class="btn-primary" @click="startExam(exam.id)">开始答题</button>
                  </div>
                </div>
              </div>
              <div v-else-if="userType === 'student' && !isLoading" class="empty-state">
                <p>暂无可参加的考试</p>
              </div>
            </div>
            
            <!-- 评价表模板标签页（仅教师端可见） -->
            <div v-if="userType === 'teacher' && examsTab === 'templates'" class="templates-content">
              <!-- 教师端：显示创建模板按钮 -->
              <div class="templates-actions">
                <button class="btn-primary" @click="handleCreateTemplateClick">创建模板</button>
              </div>
              
              <div v-if="evaluationTemplates.length > 0" class="templates-list">
                <div v-for="template in evaluationTemplates" :key="template.id" class="template-item">
                  <div class="template-info">
                    <h4>{{ template.template_name }} {{ template.is_default ? '(系统默认)' : '' }}</h4>
                    <p>{{ template.description }}</p>
                    <p>创建时间：{{ formatTime(template.created_at) }}</p>
                  </div>
                  <div class="template-actions">
                    <button class="btn-text" @click="viewTemplateDetails(template.id)">查看详情</button>
                    <!-- 教师端：非默认模板可删除 -->
                    <button v-if="!template.is_default" class="btn-text delete-btn" @click="deleteTemplate(template.id)">删除</button>
                  </div>
                </div>
              </div>
              <div v-else-if="!isLoading" class="empty-state">
                <p>暂无评价表模板</p>
              </div>
            </div>
          </div>
          <!-- 消息中心模块 -->
          <div v-if="currentFunction === 'messages'" class="messages-page">
            <div class="messages-header">
              <h2>消息中心</h2>
              <button v-if="unreadCount > 0" class="btn-text mark-all-read-btn" @click="markAllAsRead">
                全部标记已读 ({{ unreadCount }})
              </button>
            </div>

            <div class="messages-content">
              <!-- 加载状态 -->
              <div v-if="isLoadingNotifications" class="loading-state">
                <p>加载通知中...</p>
              </div>

              <!-- 有通知时显示列表 -->
              <div v-else-if="notifications.length > 0" class="notifications-list">
                <div
                  v-for="notif in notifications"
                  :key="notif.id"
                  :class="['notification-item', { 'unread': !notif.is_read }]"
                  @click="viewNotification(notif)"
                >
                  <!-- 左侧竖线（仅未读显示） -->
                  <div v-if="!notif.is_read" class="unread-indicator"></div>

                  <!-- 通知内容 -->
                  <div class="notification-content">
                    <div class="notification-header">
                      <h4 :class="{ 'unread-title': !notif.is_read }">{{ notif.title }}</h4>
                      <span v-if="!notif.is_read" class="unread-tag">未读</span>
                    </div>
                    <p class="notification-body">{{ notif.content }}</p>
                    <div class="notification-footer">
                      <span class="sender-name">{{ notif.sender_name }}</span>
                      <span class="time">{{ formatTime(notif.created_at) }}</span>
                    </div>
                  </div>
                </div>

                <!-- 分页控件 -->
                <div v-if="totalPages > 1" class="pagination">
                  <button @click="prevPage" :disabled="currentPage === 1">上一页</button>
                  <span>{{ currentPage }}/{{ totalPages }}</span>
                  <button @click="nextPage" :disabled="currentPage === totalPages">下一页</button>
                </div>
              </div>

              <!-- 无通知时显示空状态 -->
              <div v-else class="empty-notifications">
                <p>暂无通知</p>
              </div>
            </div>
          </div>
      </div>

      <!-- ==================== 个人中心页面 ==================== -->
      <div v-if="showMyPage" class="function-page">
         <div class="page-header">
          <h2>个人中心</h2>
        </div>
        <div class="card page-content">
          <!-- 标签页导航 -->
          <div class="profile-tabs">
            <button class="tab-btn active">基本资料</button>
            <button class="tab-btn">修改头像</button>
            <button class="tab-btn">密码管理</button>
            <button class="tab-btn">注销账号</button>
            <button class="tab-btn">语言</button>
          </div>
          
          <!-- 基本资料内容 -->
          <div class="profile-content">
            <div class="profile-item">
              <div class="profile-row">
                <span class="profile-label">姓名：</span>
                <span class="profile-value">{{ userName || '未设置' }}</span>
              </div>
            </div>
            
            <div class="profile-item">
              <div class="profile-row">
                <span class="profile-label">id：</span>
                <span class="profile-value">{{ userId || '未设置' }}</span>
              </div>
            </div>
            
            <div class="profile-item">
              <div class="profile-row">
                <span class="profile-label">性别：</span>
                <span class="profile-value">
                  <label class="radio-label">
                    <input type="radio" v-model="userGender" value="male" checked>
                    <span>男</span>
                  </label>
                  <label class="radio-label">
                    <input type="radio" v-model="userGender" value="female">
                    <span>女</span>
                  </label>
                </span>
              </div>
            </div>
            
            <div class="profile-item">
              <div class="profile-row">
                <span class="profile-label">手机号：</span>
                <span class="profile-value">
                  {{ currentPhone }}
                  <button class="edit-btn">修改</button>
                </span>
              </div>
            </div>
            
            <div class="profile-item">
              <div class="profile-row">
                <span class="profile-label">单位：</span>
                <span class="profile-value">
                  <button class="add-btn">+添加单位</button>
                </span>
              </div>
            </div>
            
            <div v-if="userUnit" class="profile-item">
              <div class="profile-row">
                <span class="profile-label"></span>
                <span class="profile-value unit-info">
                  {{ userUnit }}
                  <div class="unit-id">{{ userStudentId || '学号/工号: 未设置' }}</div>
                </span>
              </div>
            </div>
          </div>
          
          <!-- 退出登录按钮 -->
          <div class="profile-actions">
            <button class="logout-btn" @click="logout">退出登录</button>
          </div>
        </div>
      </div>

    </main>

    <div v-if="showProfile" class="modal-overlay">
      <LoginOrRegister @login-success="handleLoginSuccess" />
    </div>
    
    <!-- 创建班级弹窗 -->
    <div v-if="showCreateClassModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>创建新班级</h3>
          <button class="close-btn" @click="showCreateClassModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>班级名称 <span class="required">*</span></label>
            <input v-model="newClassName" type="text" class="modern-input" placeholder="请输入班级名称">
          </div>
          <div class="form-group">
            <label>班级简介</label>
            <textarea v-model="newClassDescription" class="modern-textarea" placeholder="请输入班级简介"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-text" @click="showCreateClassModal = false">取消</button>
          <button class="btn-primary" @click="createClass" :disabled="isLoading || !newClassName.trim()">
            {{ isLoading ? '创建中...' : '创建班级' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 班级详情弹窗（学生列表） -->
    <div v-if="showClassDetailModal" class="modal-overlay">
      <div class="modal-content class-detail-modal">
        <div class="modal-header">
          <h3>{{ selectedClass?.class_name }} - 学生列表</h3>
          <button class="close-btn" @click="showClassDetailModal = false">×</button>
        </div>
        <div class="modal-body">
          <div v-if="classMembers.length > 0" class="student-list">
            <div v-for="member in classMembers" :key="member.student_id" class="student-item">
              <div class="student-info">
                <p>{{ member.student_id }}</p>
                <p>加入时间：{{ formatTime(member.joined_at) }}</p>
              </div>
            </div>
          </div>
          <div v-else-if="!isLoading" class="empty-state">
            <p>该班级暂无学生</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-primary" @click="showClassDetailModal = false">关闭</button>
        </div>
      </div>
    </div>
    
    <!-- 添加学生弹窗 -->
    <div v-if="showAddStudentModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>添加学生</h3>
          <button class="close-btn" @click="showAddStudentModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>学生ID <span class="required">*</span></label>
            <input v-model="newStudentId" type="text" class="modern-input" placeholder="请输入学生ID">
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-text" @click="showAddStudentModal = false">取消</button>
          <button class="btn-primary" @click="addStudent" :disabled="isLoading || !newStudentId.trim()">
            {{ isLoading ? '添加中...' : '添加学生' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 批量导入学生弹窗 -->
    <div v-if="showImportStudentsModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>批量导入学生</h3>
          <button class="close-btn" @click="showImportStudentsModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>学生ID列表 <span class="required">*</span></label>
            <textarea 
              v-model="importStudentsText" 
              class="modern-textarea" 
              placeholder="请输入学生ID，每个ID占一行"
              rows="8"
            ></textarea>
            <p class="form-hint">示例：<br>2023001<br>2023002<br>2023003</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-text" @click="showImportStudentsModal = false">取消</button>
          <button class="btn-primary" @click="importStudents" :disabled="isLoading || !importStudentsText.trim()">
            {{ isLoading ? '导入中...' : '批量导入' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 发布考试弹窗 -->
    <div v-if="showCreateExamModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>发布考试</h3>
          <button class="close-btn" @click="showCreateExamModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>考试名称 <span class="required">*</span></label>
            <input v-model="newExam.exam_name" type="text" class="modern-input" placeholder="请输入考试名称">
          </div>
          <div class="form-group">
            <label>考试描述</label>
            <textarea v-model="newExam.description" class="modern-textarea" placeholder="请输入考试描述"></textarea>
          </div>
          <div class="form-group">
            <label>选择班级 <span class="required">*</span></label>
            <select v-model="newExam.class_id" class="modern-select">
              <option value="">请选择班级</option>
              <option v-for="cls in teacherClasses" :key="cls.id" :value="cls.id">
                {{ cls.class_name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>开始时间</label>
            <input v-model="newExam.start_time" type="datetime-local" class="modern-input">
          </div>
          <div class="form-group">
            <label>结束时间</label>
            <input v-model="newExam.end_time" type="datetime-local" class="modern-input">
          </div>
          <div class="form-group">
            <label>评价表模板</label>
            <select v-model="newExam.template_id" class="modern-select">
              <option value="">请选择模板（可选）</option>
              <option v-for="template in evaluationTemplates" :key="template.id" :value="template.id">
                {{ template.template_name }} {{ template.is_default ? '(系统默认)' : '' }}
              </option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-text" @click="showCreateExamModal = false">取消</button>
          <button class="btn-primary" @click="createExam" :disabled="isLoading || !newExam.exam_name.trim() || !newExam.class_id">
            {{ isLoading ? '发布中...' : '发布考试' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 创建评价表模板弹窗 -->
    <div v-if="showCreateTemplateModal" class="modal-overlay">
      <div class="modal-content template-modal">
        <div class="modal-header">
          <h3>创建评价表模板</h3>
          <button class="close-btn" @click="showCreateTemplateModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>模板名称 <span class="required">*</span></label>
            <input v-model="newTemplate.template_name" type="text" class="modern-input" placeholder="请输入模板名称">
          </div>
          <div class="form-group">
            <label>模板描述</label>
            <textarea v-model="newTemplate.description" class="modern-textarea" placeholder="请输入模板描述"></textarea>
          </div>
          
          <!-- 大类步骤 -->
          <div class="form-group">
            <label>评价步骤 <span class="required">*</span></label>
            <div v-for="(step, stepIndex) in newTemplate.steps" :key="stepIndex" class="step-container">
              <div class="step-header">
                <h4>步骤 {{ stepIndex + 1 }}</h4>
                <button class="btn-text delete-btn" @click="removeStep(stepIndex)">删除步骤</button>
              </div>
              <div class="form-group">
                <label>步骤名称</label>
                <input v-model="step.step_name" type="text" class="modern-input" placeholder="请输入步骤名称">
              </div>
              
              <!-- 评分点 -->
              <div class="score-points-container">
                <div class="score-points-header">
                  <h5>评分点</h5>
                  <button class="btn-text" @click="addScorePoint(stepIndex)">添加评分点</button>
                </div>
                <div v-for="(point, pointIndex) in step.score_points" :key="pointIndex" class="score-point-item">
                  <div class="form-row">
                    <div class="form-group half">
                      <label>评分点名称</label>
                      <input v-model="point.point_name" type="text" class="modern-input" placeholder="请输入评分点名称">
                    </div>
                    <div class="form-group quarter">
                      <label>分值</label>
                      <input v-model.number="point.score" type="number" class="modern-input" placeholder="0">
                    </div>
                    <div class="form-group quarter">
                      <button class="btn-text delete-btn" @click="removeScorePoint(stepIndex, pointIndex)">删除</button>
                    </div>
                  </div>
                  <div class="form-group">
                    <label>扣分点说明</label>
                    <textarea v-model="point.deduction_description" class="modern-textarea" placeholder="请输入扣分点说明"></textarea>
                  </div>
                </div>
                <div v-if="step.score_points.length === 0" class="empty-state">
                  <p>请添加评分点</p>
                </div>
              </div>
            </div>
            <button class="btn-text add-step-btn" @click="addStep">添加步骤</button>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-text" @click="showCreateTemplateModal = false">取消</button>
          <button class="btn-primary" @click="createTemplate" :disabled="isLoading || !newTemplate.template_name.trim() || newTemplate.steps.length === 0">
            {{ isLoading ? '创建中...' : '创建模板' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.score-points-card {
  margin-top: 20px;
  max-height: 600px;
  overflow-y: auto;
}

.step-score-points {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e0e0e0;
}

.step-score-points:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.step-score-points h5 {
  margin: 0 0 10px 0;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.step-score-points ul {
  margin: 0;
  padding-left: 0;
  list-style: none;
}

.step-score-points li {
  margin-bottom: 8px;
  padding-left: 25px;
  position: relative;
  font-size: 13px;
  line-height: 1.4;
}

.step-score-points li.pass {
  color: #4caf50;
}

.step-score-points li.fail {
  color: #f44336;
}

.status-icon {
  position: absolute;
  left: 0;
  top: 0;
  font-size: 16px;
  font-weight: bold;
}

.point-name {
  margin-right: 10px;
}

.point-score {
  font-size: 12px;
  color: #666;
  font-weight: 500;
  margin-right: 8px;
}

.deduction {
  margin-left: 8px;
  font-size: 12px;
  color: #f44336;
  font-weight: 500;
}

.error-explanation {
  margin-top: 5px;
  padding: 8px;
  background-color: #fff3f3;
  border-left: 3px solid #f44336;
  font-size: 12px;
  color: #d32f2f;
  border-radius: 4px;
  margin-left: 25px;
}

.step-score {
  font-size: 12px;
  color: #666;
  font-weight: 500;
  margin-left: 10px;
}

.no-points {
  font-size: 13px;
  color: #999;
  font-style: italic;
  margin: 0;
}

/* 总体评价样式 */
.summary-text {
  font-size: 14px;
  line-height: 1.6;
  color: #333;
  margin: 10px 0 0 0;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 6px;
  border-left: 3px solid #1890ff;
}

/* 标签页样式 */
.tab-buttons {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.tab-btn {
  padding: 10px 20px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 14px;
  color: #666;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
}

.tab-btn.active {
  color: #1890ff;
  border-bottom-color: #1890ff;
}

/* 考试和模板操作区域 */
.exams-actions,
.templates-actions {
  margin-bottom: 20px;
}

/* 模板列表样式 */
.templates-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.template-item {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s ease;
}

.template-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.template-info h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.template-info p {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #666;
  line-height: 1.4;
}

.template-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}

/* 考试列表样式 */
.exams-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.exam-item {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s ease;
}

.exam-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.exam-info h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.exam-info p {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #666;
  line-height: 1.4;
}

.exam-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}

/* 模板创建弹窗样式 */
.template-modal {
  width: 800px;
  max-width: 90vw;
  max-height: 80vh;
  overflow-y: auto;
}

.step-container {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  background: #f9f9f9;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.step-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.score-points-container {
  margin-top: 20px;
  border-top: 1px solid #e0e0e0;
  padding-top: 20px;
}

.score-points-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.score-points-header h5 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.score-point-item {
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 15px;
  background: #fff;
}

.form-row {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.form-group.half {
  flex: 2;
}

.form-group.quarter {
  flex: 1;
}

.add-step-btn {
  margin-top: 10px;
  display: inline-block;
}

.empty-state {
  text-align: center;
  padding: 20px;
  color: #999;
  font-style: italic;
}

/* 得失分详情样式 */
.score-points-card {
  margin-top: 0;
}

.step-score-points {
  margin-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 20px;
}

.step-score-points:last-child {
  border-bottom: none;
}

.step-score-points h5 {
  margin: 0 0 10px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.score-points-list {
  margin-left: 20px;
}

.score-point-item {
  display: flex;
  flex-direction: column;
  margin-bottom: 10px;
  padding: 10px;
  border-radius: 4px;
  background-color: #f9f9f9;
}

.score-point-item.success {
  border-left: 4px solid #4caf50;
  background-color: #f1f8e9;
}

.score-point-item.fail {
  border-left: 4px solid #f44336;
  background-color: #ffebee;
}

.score-point-item.warning {
  border-left: 4px solid #ff9800;
  background-color: #fff3e0;
}

.score-point-header {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}

.status-icon {
  font-size: 16px;
  font-weight: bold;
  margin-right: 10px;
  min-width: 20px;
}

.status-icon::before {
  content: '';
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  text-align: center;
  line-height: 16px;
  font-size: 12px;
}

.score-point-item.success .status-icon::before {
  content: '✓';
  background-color: #4caf50;
  color: white;
}

.score-point-item.fail .status-icon::before {
  content: '✗';
  background-color: #f44336;
  color: white;
}

.score-point-item.warning .status-icon::before {
  content: '!';
  background-color: #ff9800;
  color: white;
}

.point-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.point-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.point-description {
  font-size: 13px;
  color: #666;
  line-height: 1.4;
}

.point-score {
  font-weight: 600;
  margin-left: 10px;
  color: #333;
}

.deduction {
  margin-left: 10px;
  font-size: 12px;
  color: #f44336;
}

.error-explanation {
  margin-top: 5px;
  padding: 5px 10px;
  background-color: rgba(244, 67, 54, 0.1);
  border-radius: 4px;
  font-size: 13px;
  color: #d32f2f;
  margin-left: 30px;
}

.no-points {
  color: #999;
  font-style: italic;
  margin-left: 20px;
}

/* ==================== 消息中心样式 ==================== */
.messages-page {
  width: 100%;
  overflow: hidden;
}

.messages-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #E2E8F0;
}

.mark-all-read-btn {
  color: #1890ff;
  font-weight: 600;
  font-size: 14px;
}

.messages-content {
  width: 100%;
}

.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 600px;
  overflow-y: auto;
  padding-right: 8px;
}

.notification-item {
  display: flex;
  padding: 16px 20px;
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.notification-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

/* 未读状态特殊样式 */
.notification-item.unread {
  background: #f0f9ff;
  border-left: 4px solid #1890ff;
}

.unread-indicator {
  width: 4px;
  background: #1890ff;
  border-radius: 2px;
  margin-right: 16px;
  flex-shrink: 0;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.notification-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #64748b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: calc(100% - 60px);
}

.notification-header .unread-title {
  font-weight: 700;
  color: #1e293b;
}

.unread-tag {
  display: inline-block;
  padding: 2px 8px;
  background: #ff4d4f;
  color: white;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.notification-body {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #475569;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.notification-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #94a3b8;
}

.sender-name {
  font-weight: 500;
}

.time {
  font-size: 11px;
}

.empty-notifications,
.loading-state {
  text-align: center;
  padding: 60px 20px;
  color: #94a3b8;
  background: #f9fafb;
  border-radius: 12px;
  border: 1px dashed #E2E8F0;
}

/* 分页控件 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #E2E8F0;
}

.pagination button {
  padding: 6px 16px;
  background: white;
  border: 1px solid #E2E8F0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  color: #334155;
}

.pagination button:hover:not(:disabled) {
  background: #f0f9ff;
  border-color: #1890ff;
  color: #1890ff;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination span {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

/* 侧边栏红点角标 */
.nav-item {
  position: relative;
}

.unread-badge {
  position: absolute;
  top: 4px;
  right: 8px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  background: #ff4d4f;
  color: white;
  border-radius: 9px;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: badge-bounce 0.3s ease-out;
  z-index: 10;
}

@keyframes badge-bounce {
  0% { transform: scale(0); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}
</style>

<script>
import LoginOrRegister from "./LoginOrRegister.vue";
import request from './utils/request';
import evaluate1 from './assets/evaluate1.png';
import evaluate2 from './assets/evaluate2.png';

export default {
  name: 'MainPage',
  components: { LoginOrRegister },
  // ==================== 数据定义模块 ====================
  data() {
    return {
      evaluate1,
      evaluate2,
      isSidebarCollapsed: false,
      isLoggedIn: false,
      showProfile: true,
      showMyPage: false,
      currentFunction: null,
      isLoading: false,
      currentPhone: '',
      userId: '',
      userName: '',
      userGender: 'male',
      userUnit: '',
      userStudentId: '',
      userType: 'student', // 默认学生类型
      historyConversations: [],
      currentConversationId: null,
      selectedVideoURL: null,
      selectedFile: null,
      selectedFiles: [], // 教师批量上传文件
      reportData: null,
      customExperimentName: '',
      experimentNameError: '',

      functionTitles: {
        messages: '消息中心',
        exams: '考试系统',
        classes: '班级管理'
      },
      // 班级管理相关变量
      newClassName: '',
      newClassDescription: '',
      joinClassCode: '',
      teacherClasses: [],
      studentClasses: [],
      showCreateClassModal: false,
      showClassDetailModal: false,
      showAddStudentModal: false,
      showImportStudentsModal: false,
      selectedClass: null,
      classMembers: [],
      isClassDetailPage: false,
      searchKeyword: '',
      newStudentId: '',
      importStudentsText: '',
      // 考试系统相关变量
      teacherExams: [],
      studentExams: [], // 学生端考试列表
      showCreateExamModal: false,
      evaluationTemplates: [],
      examsTab: 'exams', // 'exams' 或 'templates'
      showCreateTemplateModal: false,
      newTemplate: {
        template_name: '',
        description: '',
        steps: [{
          step_name: '',
          score_points: [{
            point_name: '',
            score: 0,
            deduction_description: ''
          }]
        }]
      },
      newExam: {
        exam_name: '',
        description: '',
        class_id: '',
        template_id: '',
        start_time: '',
        end_time: ''
      },
      contextMenu: {
        visible: false,
        x: 0,
        y: 0,
        targetItem: null
      },
      // 消息中心相关数据
      notifications: [],
      unreadCount: 0,
      isLoadingNotifications: false,
      currentPage: 1,
      totalPages: 1,
      unreadTimer: null
    };
  },
  // ==================== 计算属性模块 ====================
  computed: {
    maskedPhone() {
      if (!this.currentPhone) return '';
      if (this.currentPhone.length !== 11) return this.currentPhone;
      return this.currentPhone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
    },
    filteredTeacherClasses() {
      if (!this.searchKeyword) return this.teacherClasses;
      const keyword = this.searchKeyword.toLowerCase();
      return this.teacherClasses.filter(cls => 
        cls.class_name.toLowerCase().includes(keyword)
      );
    }
  },
  // ==================== 生命周期钩子模块 ====================
  async created() {
    const token = localStorage.getItem('token');
    if (token) {
      this.isLoggedIn = true;
      this.showProfile = false;
      try {
        await this.loadUserInfo();
        await this.loadHistoryList();
        // 启动未读数轮询
        this.startUnreadPolling();
      } catch (error) {
        console.error('初始化加载失败:', error);
      }
    } else {
      this.isLoggedIn = false;
      this.showProfile = true;
    }
  },
  beforeDestroy() {
    // 清理定时器防止内存泄漏
    this.stopUnreadPolling();
  },
  // ==================== 方法模块 ====================
  methods: {
    // ==================== 工具方法 ====================
    formatTime(dateStr) {
      if (!dateStr) return '';
      
      let date;
      if (typeof dateStr === 'string') {
        date = new Date(dateStr);
      } else if (dateStr instanceof Date) {
        date = dateStr;
      } else {
        return '';
      }
      
      if (isNaN(date.getTime())) {
        return '';
      }
      
      const now = new Date();
      const diffMs = now - date;
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMs / 3600000);
      const diffDays = Math.floor(diffMs / 86400000);

      if (diffMins < 1) return '刚刚';
      if (diffMins < 60) return `${diffMins}分钟前`;
      if (diffHours < 24) return `${diffHours}小时前`;
      if (diffDays < 7) return `${diffDays}天前`;
      return `${date.getMonth() + 1}/${date.getDate()}`;
    },
    // ==================== 上下文菜单相关方法 ====================
    showContextMenu(e, item) {
      this.contextMenu.x = e.clientX;
      this.contextMenu.y = e.clientY;
      this.contextMenu.targetItem = item;
      this.contextMenu.visible = true;
    },
    hideContextMenu() {
      this.contextMenu.visible = false;
    },
    async handleDelete() {
      if (!this.contextMenu.targetItem) return;
      if (confirm(`确认删除记录 "${this.contextMenu.targetItem.title}" 吗？`)) {
        this.historyConversations = this.historyConversations.filter(i => i.id !== this.contextMenu.targetItem.id);
        if (this.currentConversationId === this.contextMenu.targetItem.id) {
          this.resetDashboard();
        }
      }
      this.hideContextMenu();
    },
    async handleRename() {
      if (!this.contextMenu.targetItem) return;
      const newName = prompt("请输入新的实验名称", this.contextMenu.targetItem.title);
      if (newName && newName.trim() !== "") {
        this.contextMenu.targetItem.title = newName;
      }
      this.hideContextMenu();
    },
    // ==================== 用户认证相关方法 ====================
    async handleLoginSuccess() {
      this.showProfile = false;
      this.isLoggedIn = true;
      this.currentPhone = localStorage.getItem('userPhone');
      this.userType = localStorage.getItem('userType') || 'student';
      this.userId = localStorage.getItem('userId');
      await this.loadHistoryList();
      // 启动未读数定时轮询
      this.startUnreadPolling();
    },
    
    // 加载用户信息
    async loadUserInfo() {
      if (!this.isLoggedIn) return;
      try {
        const response = await request.get('users/me');
        this.userId = response.user_id;
        this.userName = response.name;
        this.currentPhone = response.user_phone;
        this.userType = response.user_type;
        // 更新localStorage
        localStorage.setItem('userId', response.user_id);
        localStorage.setItem('userPhone', response.user_phone);
        localStorage.setItem('userType', response.user_type);
      } catch (error) {
        console.error('加载用户信息失败:', error);
      }
    },
    toggleSidebar() { this.isSidebarCollapsed = !this.isSidebarCollapsed; },
    
    // 检查登录状态
    checkLoginStatus() {
      const token = localStorage.getItem('token');
      if (!token) {
        localStorage.clear();
        this.isLoggedIn = false;
        this.showProfile = true;
        alert('登录过期，请重新登录！');
        return false;
      }
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        if (Date.now() > payload.exp * 1000) {
          localStorage.clear();
          this.isLoggedIn = false;
          this.showProfile = true;
          alert('登录过期，请重新登录！');
          return false;
        }
      } catch (error) {
        localStorage.clear();
        this.isLoggedIn = false;
        this.showProfile = true;
        alert('登录过期，请重新登录！');
        return false;
      }
      return true;
    },
    
    selectFunction(func) {
      // 检查登录状态
      if (!this.checkLoginStatus()) return;

      this.currentFunction = func;
      this.showMyPage = false;
      // 当切换到班级管理页面时加载班级列表
      if (func === 'classes') {
        this.loadClassList();
      }
      // 当切换到考试系统页面时加载考试列表、班级列表和评价表模板
      if (func === 'exams') {
        this.loadExamList();
        this.loadClassList();
        this.loadEvaluationTemplates();
      }
      // 当切换到消息中心页面时加载通知列表
      if (func === 'messages') {
        this.loadNotifications();
        this.loadUnreadCount();
      }
    },
    async showMy() { 
      // 检查登录状态
      if (!this.checkLoginStatus()) return;
      
      this.showMyPage = true; 
      this.currentFunction = null; 
      await this.loadUserInfo();
    },
    
    // 加载班级列表
    async loadClassList() {
      if (!this.isLoggedIn) return;
      try {
        if (this.userType === 'teacher') {
          // 教师加载自己创建的班级
          this.teacherClasses = await request.get('classes');
        } else {
          // 学生加载自己加入的班级
          this.studentClasses = await request.get('student/classes');
        }
      } catch (error) {
        console.error('加载班级列表失败:', error);
      }
    },
    
    // 创建班级（教师）
    async createClass() {
      if (!this.isLoggedIn) {
        this.showProfile = true;
        return;
      }
      if (!this.newClassName.trim()) return;
      try {
        this.isLoading = true;
        const response = await request.post('classes', { 
          class_name: this.newClassName,
          description: this.newClassDescription
        });
        // 移除弹窗提示
        this.newClassName = '';
        this.newClassDescription = '';
        this.showCreateClassModal = false;
        // 重新加载班级列表
        await this.loadClassList();
      } catch (error) {
        console.error('创建班级失败:', error);
        // 移除弹窗提示
      } finally {
        this.isLoading = false;
      }
    },
    
    // 进入班级详情（查看学生列表）
    async enterClassDetail(classId) {
      try {
        this.isLoading = true;
        const response = await request.get(`classes/${classId}`);
        this.selectedClass = response;
        this.classMembers = response.members;
        this.isClassDetailPage = true;
      } catch (error) {
        console.error('获取班级详情失败:', error);
        alert('获取班级详情失败，请重试');
      } finally {
        this.isLoading = false;
      }
    },
    
    // 删除学生
    async removeStudent(studentId) {
      if (!this.isLoggedIn) {
        this.showProfile = true;
        return;
      }
      if (confirm('确定要移除这个学生吗？')) {
        try {
          this.isLoading = true;
          await request.delete(`classes/${this.selectedClass.id}/students/${studentId}`);
          // 重新加载班级详情
          await this.enterClassDetail(this.selectedClass.id);
        } catch (error) {
          console.error('删除学生失败:', error);
          alert('删除学生失败，请重试');
        } finally {
          this.isLoading = false;
        }
      }
    },
    
    // 添加学生
    async addStudent() {
      if (!this.isLoggedIn) {
        this.showProfile = true;
        return;
      }
      if (!this.newStudentId.trim()) return;
      try {
        this.isLoading = true;
        await request.post(`classes/${this.selectedClass.id}/students`, {
          student_id: this.newStudentId
        });
        // 重新加载班级详情
        await this.enterClassDetail(this.selectedClass.id);
        this.newStudentId = '';
        this.showAddStudentModal = false;
      } catch (error) {
        console.error('添加学生失败:', error);
        alert('添加学生失败，请重试');
      } finally {
        this.isLoading = false;
      }
    },
    
    // 批量导入学生
    async importStudents() {
      if (!this.isLoggedIn) {
        this.showProfile = true;
        return;
      }
      if (!this.importStudentsText.trim()) return;
      try {
        this.isLoading = true;
        const studentIds = this.importStudentsText.split('\n')
          .map(id => id.trim())
          .filter(id => id);
        
        for (const studentId of studentIds) {
          try {
            await request.post(`classes/${this.selectedClass.id}/students`, {
              student_id: studentId
            });
          } catch (error) {
            console.error(`添加学生 ${studentId} 失败:`, error);
          }
        }
        
        // 重新加载班级详情
        await this.enterClassDetail(this.selectedClass.id);
        this.importStudentsText = '';
        this.showImportStudentsModal = false;
      } catch (error) {
        console.error('批量导入学生失败:', error);
        alert('批量导入学生失败，请重试');
      } finally {
        this.isLoading = false;
      }
    },
    
    // 返回班级列表
    backToClassList() {
      this.isClassDetailPage = false;
      this.selectedClass = null;
      this.classMembers = [];
    },
    
    // 处理创建班级按钮点击
    handleCreateClassClick() {
      if (!this.isLoggedIn) {
        this.showProfile = true;
        return;
      }
      this.showCreateClassModal = true;
    },
    
    // 处理发布考试按钮点击
    async handleCreateExamClick() {
      if (!this.isLoggedIn) {
        this.showProfile = true;
        return;
      }
      // 确保班级列表已加载
      try {
        console.log('开始加载班级列表...');
        await this.loadClassList();
        console.log('班级列表加载完成:', this.teacherClasses);
        if (this.teacherClasses.length === 0) {
          alert('您还没有创建班级，请先创建班级后再发布考试');
          return;
        }
        this.showCreateExamModal = true;
      } catch (error) {
        console.error('加载班级列表失败:', error);
        alert('加载班级列表失败，请重试');
      }
    },
    
    // 处理创建模板按钮点击
    handleCreateTemplateClick() {
      if (!this.isLoggedIn) {
        this.showProfile = true;
        return;
      }
      // 重置模板数据
      this.newTemplate = {
        template_name: '',
        description: '',
        steps: [{
          step_name: '',
          score_points: [{
            point_name: '',
            score: 0,
            deduction_description: ''
          }]
        }]
      };
      this.showCreateTemplateModal = true;
    },
    
    // 添加步骤
    addStep() {
      this.newTemplate.steps.push({
        step_name: '',
        score_points: [{
          point_name: '',
          score: 0,
          deduction_description: ''
        }]
      });
    },
    
    // 删除步骤
    removeStep(stepIndex) {
      if (this.newTemplate.steps.length > 1) {
        this.newTemplate.steps.splice(stepIndex, 1);
      }
    },
    
    // 添加评分点
    addScorePoint(stepIndex) {
      this.newTemplate.steps[stepIndex].score_points.push({
        point_name: '',
        score: 0,
        deduction_description: ''
      });
    },
    
    // 删除评分点
    removeScorePoint(stepIndex, pointIndex) {
      if (this.newTemplate.steps[stepIndex].score_points.length > 1) {
        this.newTemplate.steps[stepIndex].score_points.splice(pointIndex, 1);
      }
    },
    
    // 创建评价表模板
    async createTemplate() {
      if (!this.isLoggedIn) {
        this.showProfile = true;
        return;
      }
      if (!this.newTemplate.template_name.trim()) {
        alert('请填写模板名称');
        return;
      }
      if (this.newTemplate.steps.length === 0) {
        alert('请添加至少一个评价步骤');
        return;
      }
      try {
        this.isLoading = true;
        // 1. 创建模板
        const templateResponse = await request.post('templates', {
          template_name: this.newTemplate.template_name,
          description: this.newTemplate.description
        });
        const templateId = templateResponse.id;
        
        // 2. 添加步骤和评分点
        for (let i = 0; i < this.newTemplate.steps.length; i++) {
          const step = this.newTemplate.steps[i];
          if (!step.step_name.trim()) {
            throw new Error(`请填写步骤 ${i + 1} 的名称`);
          }
          
          // 创建步骤
          const stepResponse = await request.post(`templates/${templateId}/steps`, {
            step_name: step.step_name,
            step_order: i + 1
          });
          const stepId = stepResponse.id;
          
          // 添加评分点
          for (let j = 0; j < step.score_points.length; j++) {
            const point = step.score_points[j];
            if (!point.point_name.trim()) {
              throw new Error(`请填写步骤 ${i + 1} 中评分点 ${j + 1} 的名称`);
            }
            if (point.score === undefined || point.score < 0) {
              throw new Error(`请为步骤 ${i + 1} 中评分点 ${j + 1} 设置有效的分值`);
            }
            if (!point.deduction_description.trim()) {
              throw new Error(`请填写步骤 ${i + 1} 中评分点 ${j + 1} 的扣分点说明`);
            }
            
            await request.post(`templates/steps/${stepId}/score-points`, {
              point_name: point.point_name,
              point_order: j + 1,
              score: point.score,
              deduction_description: point.deduction_description
            });
          }
        }
        
        // 重新加载模板列表
        await this.loadEvaluationTemplates();
        // 清空表单
        this.newTemplate = {
          template_name: '',
          description: '',
          steps: [{
            step_name: '',
            score_points: [{
              point_name: '',
              score: 0,
              deduction_description: ''
            }]
          }]
        };
        this.showCreateTemplateModal = false;
        // 显示成功提示
        alert('模板创建成功！');
      } catch (error) {
        console.error('创建模板失败:', error);
        alert(`创建模板失败: ${error.message || '未知错误'}`);
      } finally {
        this.isLoading = false;
      }
    },
    
    // 查看模板详情
    async viewTemplateDetails(templateId) {
      try {
        this.isLoading = true;
        const response = await request.get(`templates/${templateId}`);
        // 这里可以显示模板详情，暂时使用alert
        alert(`模板详情：${response.template_name}\n${response.description}`);
      } catch (error) {
        console.error('获取模板详情失败:', error);
        alert('获取模板详情失败，请重试');
      } finally {
        this.isLoading = false;
      }
    },
    
    // 删除模板
    async deleteTemplate(templateId) {
      if (!this.isLoggedIn) {
        this.showProfile = true;
        return;
      }
      if (confirm('确定要删除这个模板吗？')) {
        try {
          this.isLoading = true;
          await request.delete(`templates/${templateId}`);
          // 重新加载模板列表
          await this.loadEvaluationTemplates();
        } catch (error) {
          console.error('删除模板失败:', error);
          alert('删除模板失败，请重试');
        } finally {
          this.isLoading = false;
        }
      }
    },
    
    // 处理搜索
    handleSearch() {
      // 搜索逻辑已在计算属性中实现
    },
    
    // 加入班级（学生）
    async joinClass() {
      if (!this.isLoggedIn) {
        this.showProfile = true;
        return;
      }
      if (!this.joinClassCode.trim()) return;
      try {
        this.isLoading = true;
        const response = await request.post('classes/join', { class_code: this.joinClassCode });
        // 移除弹窗提示
        this.joinClassCode = '';
        // 重新加载班级列表
        await this.loadClassList();
      } catch (error) {
        console.error('加入班级失败:', error);
      } finally {
        this.isLoading = false;
      }
    },
    
    // 复制班级号
    copyClassCode(classCode) {
      navigator.clipboard.writeText(classCode).then(() => {
        // 移除弹窗提示
      }).catch(err => {
        console.error('复制失败:', err);
        // 移除弹窗提示
      });
    },
    
    // 加载考试列表
    async loadExamList() {
      if (!this.isLoggedIn) return;
      try {
        if (this.userType === 'teacher') {
          // 教师加载自己发布的考试
          this.teacherExams = await request.get('exams');
        } else {
          // 学生加载可参加的考试
          this.studentExams = await request.get('student/exams');
        }
      } catch (error) {
        console.error('加载考试列表失败:', error);
      }
    },
    
    // 加载评价表模板列表
    async loadEvaluationTemplates() {
      if (!this.isLoggedIn) return;
      try {
        // 只有教师可以查看评价表模板
        if (this.userType === 'teacher') {
          this.evaluationTemplates = await request.get('templates');
        }
      } catch (error) {
        console.error('加载评价表模板失败:', error);
      }
    },
    
    // 发布考试
    async createExam() {
      if (!this.isLoggedIn) {
        this.showProfile = true;
        return;
      }
      if (!this.newExam.exam_name.trim() || !this.newExam.class_id) {
        alert('请填写考试名称并选择班级');
        return;
      }
      try {
        this.isLoading = true;
        console.log('发布考试请求:', this.newExam);
        console.log('本地存储的token:', localStorage.getItem('token'));
        console.log('开始发送请求...');
        const response = await request.post('exams', {
          exam_name: this.newExam.exam_name,
          description: this.newExam.description,
          class_id: parseInt(this.newExam.class_id),
          template_id: this.newExam.template_id ? parseInt(this.newExam.template_id) : null,
          start_time: this.newExam.start_time,
          end_time: this.newExam.end_time
        });
        console.log('发布考试响应:', response);
        // 重新加载考试列表
        await this.loadExamList();
        // 清空表单
        this.newExam = {
          exam_name: '',
          description: '',
          class_id: '',
          start_time: '',
          end_time: ''
        };
        this.showCreateExamModal = false;
        // 显示成功提示
        alert('考试发布成功！');
      } catch (error) {
        console.error('发布考试失败:', error);
        console.error('错误类型:', typeof error);
        console.error('错误对象:', error);
        console.error('错误消息:', error.message);
        console.error('错误堆栈:', error.stack);
        if (error.response) {
          console.error('错误响应:', error.response);
          console.error('错误响应状态:', error.response.status);
          console.error('错误响应数据:', error.response.data);
          alert(`发布考试失败: ${error.response.data.detail || '未知错误'}`);
        } else if (error.request) {
          console.error('错误请求:', error.request);
          alert('发布考试失败，服务器无响应');
        } else {
          console.error('错误信息:', error.message);
          alert(`发布考试失败: ${error.message || '未知错误'}`);
        }
      } finally {
        this.isLoading = false;
      }
    },
    
    // 查看考试详情
    async viewExamDetails(examId) {
      try {
        this.isLoading = true;
        const response = await request.get(`exams/${examId}`);
        // 这里可以显示考试详情，暂时使用alert
        alert(`考试详情：${response.exam_name}\n${response.description}`);
      } catch (error) {
        console.error('获取考试详情失败:', error);
        alert('获取考试详情失败，请重试');
      } finally {
        this.isLoading = false;
      }
    },
    
    // 开始答题
    async startExam(examId) {
      if (!this.isLoggedIn) {
        this.showProfile = true;
        return;
      }
      try {
        this.isLoading = true;
        // 检查考试状态
        const exam = await request.get(`exams/${examId}`);
        if (exam.status === 'closed') {
          alert('考试已结束，无法参加');
          return;
        }
        
        // 跳转到答题页面或开始上传视频
        // 这里暂时显示提示，实际项目中应该跳转到答题页面
        alert(`开始参加考试：${exam.exam_name}`);
        
        // 重置仪表板，准备上传视频
        this.resetDashboard();
        this.customExperimentName = exam.exam_name;
        
      } catch (error) {
        console.error('开始考试失败:', error);
        alert('开始考试失败，请重试');
      } finally {
        this.isLoading = false;
      }
    },
    
    // 删除考试
    async deleteExam(examId) {
      if (!this.isLoggedIn) {
        this.showProfile = true;
        return;
      }
      if (confirm('确定要删除这个考试吗？')) {
        try {
          this.isLoading = true;
          await request.delete(`exams/${examId}`);
          // 重新加载考试列表
          await this.loadExamList();
        } catch (error) {
          console.error('删除考试失败:', error);
          alert('删除考试失败，请重试');
        } finally {
          this.isLoading = false;
        }
      }
    },
    
    // 解散班级
    async deleteClass(classId) {
      if (!this.isLoggedIn) {
        this.showProfile = true;
        return;
      }
      if (confirm('确定要解散这个班级吗？解散后班级内的所有学生将自动退出班级。')) {
        try {
          this.isLoading = true;
          await request.delete(`classes/${classId}`);
          // 重新加载班级列表
          await this.loadClassList();
        } catch (error) {
          console.error('解散班级失败:', error);
        } finally {
          this.isLoading = false;
        }
      }
    },

    resetDashboard() {
      this.currentFunction = null;
      this.showMyPage = false;
      this.resetSelection();
    },
    resetSelection() {
      this.reportData = null;
      this.selectedVideoURL = null;
      this.selectedFile = null;
      this.selectedFiles = [];
      this.currentConversationId = null;
      this.customExperimentName = '';
      this.experimentNameError = '';
      if (this.$refs.videoInput) this.$refs.videoInput.value = '';
    },
    logout() { localStorage.clear(); location.reload(); },
    async loadHistoryList() {
      if (!this.isLoggedIn) return;
      try {
        this.historyConversations = await request.get('conversations');
      } catch (error) {
        console.error('加载历史记录失败:', error);
      }
    },
    handleFileChange(e) {
      const files = e.target.files;
      if (!files || files.length === 0) return;
      
      if (this.userType === 'student') {
        // 学生端：单个文件上传
        const file = files[0];
        this.selectedFile = file;
        this.selectedVideoURL = URL.createObjectURL(file);
      } else {
        // 教师端：批量文件上传
        this.selectedFiles = Array.from(files);
      }
    },
    
    removeFile(index) {
      this.selectedFiles.splice(index, 1);
    },
    handleMainBtnClick() {
      // 检查登录状态
      if (!this.checkLoginStatus()) return;
      
      if (this.userType === 'student') {
        // 学生端逻辑
        if (!this.selectedFile) {
          this.$refs.videoInput.click();
        } else {
          // 验证实验名称
          if (!this.customExperimentName || this.customExperimentName.trim() === '') {
            this.experimentNameError = '请输入实验名称';
            return;
          }
          this.experimentNameError = '';
          this.startAnalysis();
        }
      } else {
        // 教师端逻辑
        if (this.selectedFiles.length === 0) {
          this.$refs.videoInput.click();
        } else {
          // 验证实验名称
          if (!this.customExperimentName || this.customExperimentName.trim() === '') {
            this.experimentNameError = '请输入实验名称';
            return;
          }
          this.experimentNameError = '';
          this.startBatchAnalysis();
        }
      }
    },
    async startAnalysis() {
      // 检查登录状态
      if (!this.checkLoginStatus()) return;
      
      if (!this.selectedFile) return;
      this.isLoading = true;
      this.reportData = null;
      try {
        console.log('开始分析视频...');
        console.log('选中的文件:', this.selectedFile);
        
        let convId = this.currentConversationId;
        const title = this.customExperimentName ? this.customExperimentName : 'AI 智能评估中...';
        if (!convId) {
          console.log('创建新对话...');
          const conv = await request.post('conversations', {title: title});
          console.log('创建对话成功:', conv);
          convId = conv.id;
          this.currentConversationId = convId;
        }
        
        console.log('准备上传视频，对话ID:', convId);
        const formData = new FormData();
        formData.append('video', this.selectedFile);
        if (this.customExperimentName) { 
          formData.append('experiment_name', this.customExperimentName); 
          console.log('实验名称:', this.customExperimentName);
        }
        
        console.log('开始上传视频...');
        const res = await request.post(`conversations/${convId}/video`, formData, {
          headers: {'Content-Type': 'multipart/form-data'},
          timeout: 180000 // 增加超时时间到3分钟
        });
        
        console.log('上传成功，响应:', res);
        if (res.ai_message && res.ai_message.content) {
          console.log('AI分析结果:', res.ai_message.content);
          this.parseAIResponse(res.ai_message.content);
          if (this.reportData) {
            this.reportData.create_time = new Date();
          }
        }
      } catch (error) {
        console.error('分析失败:', error);
        if (error.response) {
          console.error('响应错误:', error.response);
          alert(`分析失败: ${error.response.data?.detail || '服务器错误'}`);
        } else if (error.request) {
          console.error('请求错误:', error.request);
          alert('分析失败，请检查网络连接');
        } else {
          console.error('其他错误:', error.message);
          alert(`分析失败: ${error.message}`);
        }
      } finally {
        // 无论上传成功还是失败，都重新加载历史记录和对话详情
        await this.loadHistoryList();
        if (this.currentConversationId) {
          await this.loadHistory(this.currentConversationId);
        }
        this.isLoading = false;
      }
    },
    
    async startBatchAnalysis() {
      // 检查登录状态
      if (!this.checkLoginStatus()) return;
      
      if (this.selectedFiles.length === 0) return;
      
      this.isLoading = true;
      this.reportData = null;
      
      try {
        // 为每个视频创建一个新的对话并分析
        for (let i = 0; i < this.selectedFiles.length; i++) {
          const file = this.selectedFiles[i];
          const title = `${this.customExperimentName} - ${file.name}`;
          
          // 创建新对话
          const conv = await request.post('conversations', {title: title});
          const convId = conv.id;
          
          // 上传视频并分析
          const formData = new FormData();
          formData.append('video', file);
          if (this.customExperimentName) { formData.append('experiment_name', this.customExperimentName); }
          
          await request.post(`conversations/${convId}/video`, formData, {
            headers: {'Content-Type': 'multipart/form-data'},
            timeout: 120000
          });
        }
        
        // 分析完成后刷新历史记录
        await this.loadHistoryList();
        
        // 显示成功提示
        alert(`已成功提交 ${this.selectedFiles.length} 个视频进行分析`);
        
        // 重置选择
        this.resetSelection();
        
      } catch (error) {
        alert('批量分析失败，请检查网络或文件大小');
        console.error(error);
      } finally {
        this.isLoading = false;
      }
    },
    async loadHistory(id) {
      // 检查登录状态
      if (!this.checkLoginStatus()) return;
      this.currentFunction = null;
      this.showMyPage = false;
      try {
        const res = await request.get(`conversations/${id}`);
        this.currentConversationId = res.id;
        if (res.title && res.title !== '新对话' && !res.title.includes('评估中')) {
          this.customExperimentName = res.title;
        }
        const aiMsgs = res.messages.filter(m => m.sender_type === 'assistant');
        if (aiMsgs.length > 0) {
          const lastMsg = aiMsgs[aiMsgs.length - 1];
          this.parseAIResponse(lastMsg.content);

          // === 修改开始：从左侧列表中查找正确的时间 ===
          const currentItem = this.historyConversations.find(item => item.id === id);
          if (this.reportData && currentItem) {
            // 如果在列表里找到了这条记录，就用列表里的时间 (updated_at)
            this.reportData.create_time = currentItem.updated_at;
          } else if (this.reportData) {
            // 如果没找到（极少情况），保底显示当前时间
            this.reportData.create_time = new Date();
          }
          // === 修改结束 ===

        } else {
          this.reportData = null;
        }
        this.selectedVideoURL = null;
      } catch (e) { console.error(e); }
    },
    parseAIResponse(content) {
      try {
        const jsonMatch = content.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          this.reportData = JSON.parse(jsonMatch[0]);
        } else { throw new Error("No JSON found"); }
      } catch (e) {
        this.reportData = {
          total_score: 0, summary: "数据解析异常", experiment_name: "未知实验", steps: []
        };
      }
    },
    // 获取评级文字
    getScoreRating(score) {
      if (score >= 90) return '优秀';
      if (score >= 80) return '良好';
      if (score >= 60) return '及格';
      return '需改进';
    },
    // 获取评级样式类
    getScoreRatingClass(score) {
      if (score >= 90) return 'rating-high';
      if (score >= 80) return 'rating-good';
      if (score >= 60) return 'rating-mid';
      return 'rating-low';
    },
    // 获取旧版分数颜色 (保留给Timeline使用)
    getScoreClass(score) {
      if (score >= 90) return 'score-high';
      if (score >= 60) return 'score-mid';
      return 'score-low';
    },

    // ==================== 消息中心相关方法 ====================
    
    // 加载通知列表
    async loadNotifications(page = 1) {
      if (!this.isLoggedIn) return;
      try {
        this.isLoadingNotifications = true;
        const response = await request.get('notifications', {
          params: { page, page_size: 20 }
        });
        this.notifications = response.items || response;
        this.currentPage = response.page || page;
        this.totalPages = response.total_pages || 1;
      } catch (error) {
        console.error('加载通知失败:', error);
      } finally {
        this.isLoadingNotifications = false;
      }
    },
    
    // 加载未读数量
    async loadUnreadCount() {
      if (!this.isLoggedIn) return;
      try {
        const response = await request.get('notifications/unread-count');
        this.unreadCount = response.unread_count || 0;
      } catch (error) {
        console.error('获取未读数失败:', error);
      }
    },
    
    // 标记单条已读
    async markAsRead(notificationId) {
      try {
        await request.put(`notifications/${notificationId}/read`);
        // 更新本地状态
        const notif = this.notifications.find(n => n.id === notificationId);
        if (notif) {
          notif.is_read = true;
          this.unreadCount = Math.max(0, this.unreadCount - 1);
        }
      } catch (error) {
        console.error('标记已读失败:', error);
      }
    },
    
    // 全部标记已读
    async markAllAsRead() {
      try {
        const response = await request.put('notifications/read-all');
        // 批量更新本地状态
        this.notifications.forEach(n => n.is_read = true);
        this.unreadCount = 0;
      } catch (error) {
        console.error('全部标记已读失败:', error);
      }
    },
    
    // 查看通知详情
    async viewNotification(notification) {
      // 如果未读则标记为已读
      if (!notification.is_read) {
        await this.markAsRead(notification.id);
      }
      
      // 如果是考试通知，跳转到考试详情
      if (notification.notification_type === 'exam_announcement' && notification.related_id) {
        this.currentFunction = 'exams';
        this.examsTab = 'exams';
        await this.loadExamList();
        await this.viewExamDetails(notification.related_id);
      }
    },
    
    // 分页：上一页
    prevPage() {
      if (this.currentPage > 1) {
        this.loadNotifications(this.currentPage - 1);
      }
    },
    
    // 分页：下一页
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.loadNotifications(this.currentPage + 1);
      }
    },
    
    // 启动未读数定时轮询
    startUnreadPolling() {
      this.stopUnreadPolling();
      this.unreadTimer = setInterval(() => {
        if (this.isLoggedIn) {
          this.loadUnreadCount();
        }
      }, 30000); // 30秒间隔
    },
    
    // 停止轮询
    stopUnreadPolling() {
      if (this.unreadTimer) {
        clearInterval(this.unreadTimer);
        this.unreadTimer = null;
      }
    }
  }
}
</script>

<style>
/* 全局样式 */
html, body {
  margin: 0;
  padding: 0;
  overflow: hidden;
  height: 100%;
  width: 100%;
}
</style>

<style scoped>
/* 全局样式 */
.app-container {
  display: flex; height: 100vh; width: 100vw; overflow: hidden;
  background-color: #FFFFFF;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  color: #334155;
  transition: all 0.3s ease;
}

.app-container.teacher-mode {
  background-color: #FFFFFF;
  color: #1890FF;
}

.app-container.teacher-mode .sidebar {
  background-color: #FFFFFF;
  box-shadow: 4px 0 24px rgba(24, 144, 255, 0.1);
}

.app-container.teacher-mode .logo-text {
  color: #1890FF;
}

.app-container.teacher-mode .user-avatar {
  background-color: #E6F7FF;
  color: #1890FF;
}

.app-container.teacher-mode .new-conversation-btn {
  background: #1890FF;
  box-shadow: 0 6px 16px rgba(24, 144, 255, 0.2);
}

.app-container.teacher-mode .new-conversation-btn:hover {
  box-shadow: 0 10px 20px rgba(24, 144, 255, 0.3);
}

.app-container.teacher-mode .nav-item.active {
  background-color: #E6F7FF;
  color: #1890FF;
}

.app-container.teacher-mode .nav-item:hover {
  background-color: #F0F9FF;
  color: #1890FF;
}

.app-container.teacher-mode .btn-primary {
  background: #1890FF;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.2);
}

.app-container.teacher-mode .btn-primary:hover:not(:disabled) {
  background: #40A9FF;
  box-shadow: 0 8px 20px rgba(24, 144, 255, 0.3);
}

.app-container.teacher-mode .score-value {
  color: #1890FF;
}

.app-container.teacher-mode .section-title {
  border-left: 4px solid #1890FF;
}

.app-container.teacher-mode .reselect-btn {
  background: #1890FF;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.2);
}

.app-container.teacher-mode .reselect-btn:hover {
  background: #40A9FF;
  box-shadow: 0 8px 20px rgba(24, 144, 255, 0.3);
}

/* 教师模式下的上传视频框样式 */
.app-container.teacher-mode .video-area {
  background-color: #E6F7FF;
  border-color: #91D5FF;
}

.app-container.teacher-mode .video-area:hover {
  border-color: #1890FF;
  background-color: #BAE7FF;
}

.app-container.teacher-mode .video-area.has-video {
  background: white;
}

.app-container.teacher-mode .video-area.has-videos {
  background: white;
}

/* 教师模式下的批量上传容器样式 */
.app-container.teacher-mode .batch-upload-container h4 {
  color: #1890FF;
}

.app-container.teacher-mode .file-list li {
  background: #E6F7FF;
  border-color: #91D5FF;
}

.app-container.teacher-mode .remove-file-btn:hover {
  background: #FFF1F0;
}

/* 教师模式下的表单元素样式 */
.app-container.teacher-mode .card-header h3 {
  color: #1890FF;
}

.app-container.teacher-mode .status-badge {
  color: #1890FF;
  background: #E6F7FF;
}

.app-container.teacher-mode .input-group label {
  color: #1890FF;
}

.app-container.teacher-mode .modern-input {
  border-color: #91D5FF;
  background: #E6F7FF;
}

.app-container.teacher-mode .modern-input:focus {
  border-color: #1890FF;
  box-shadow: 0 0 0 4px rgba(24, 144, 255, 0.1);
}

.app-container.teacher-mode .btn-text {
  color: #1890FF;
}

.app-container.teacher-mode .btn-text:hover {
  color: #40A9FF;
}

/* 教师模式下的结果面板样式 */
.app-container.teacher-mode .result-title {
  color: #1890FF;
}

.app-container.teacher-mode .result-meta {
  color: #69C0FF;
}

.app-container.teacher-mode .step-count {
  color: #69C0FF;
  background: #E6F7FF;
}

.app-container.teacher-mode .timeline-content {
  background: #E6F7FF;
  border-color: #91D5FF;
}

.app-container.teacher-mode .step-head strong {
  color: #1890FF;
}

.app-container.teacher-mode .timeline-content p {
  color: #40A9FF;
}

.batch-upload-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  gap: 20px;
}

.batch-upload-container h4 {
  margin: 0;
  color: #334155;
}

.file-list {
  width: 100%;
  max-height: 200px;
  overflow-y: auto;
  list-style: none;
  padding: 0;
  margin: 0;
  gap: 10px;
  display: flex;
  flex-direction: column;
}

.file-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: #F8FAFC;
  border-radius: 8px;
  border: 1px solid #E2E8F0;
  font-size: 14px;
}

.remove-file-btn {
  background: none;
  border: none;
  color: #EF4444;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.remove-file-btn:hover {
  background: #FEF2F2;
  transform: scale(1.1);
}

.video-area.has-videos {
  background: white;
  border: none;
  padding: 16px;
}

/* === 滚动条美化 (Webkit) === */
::-webkit-scrollbar {
  width: 5px;
  height: 5px;
}

::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background-color: rgba(148, 163, 184, 0.3); /* Slate-400 with opacity */
  border-radius: 4px;
  transition: background-color 0.2s;
}

::-webkit-scrollbar-thumb:hover {
  background-color: rgba(148, 163, 184, 0.6);
}

/* Firefox */
* {
  scrollbar-width: thin;
  scrollbar-color: rgba(148, 163, 184, 0.3) transparent;
}

/* === 侧边栏 === */
.sidebar {
  width: 260px; background-color: #fff; display: flex; flex-direction: column;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); z-index: 20;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.02); border-right: none;
}
.sidebar.collapsed { width: 0; overflow: hidden; opacity: 0; }

.sidebar-toggle-btn {
  position: absolute; top: 24px; left: 240px; width: 32px; height: 32px;
  background-color: #fff; border: 1px solid #E2E8F0; border-radius: 50%;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); z-index: 1000; color: #64748B;
  transition: all 0.3s ease;
}
.sidebar-toggle-btn:hover { color: teal; transform: scale(1.1); box-shadow: 0 4px 12px rgba(0, 128, 128, 0.15); }
.sidebar-toggle-btn.collapsed { left: 16px; }

.sidebar-logo { padding: 24px; display: flex; align-items: center; gap: 12px; }
.logo-icon { font-size: 28px; }
.logo-text { font-size: 18px; font-weight: 800; color: teal; margin: 0; letter-spacing: -0.5px; }

.user-profile-area {
  padding: 12px 24px 24px; display: flex; align-items: center; gap: 16px;
  cursor: pointer; border-bottom: 1px solid #F1F5F9; transition: background 0.2s;
}
.user-profile-area:hover { background: #F8FAFC; }
.user-avatar {
  width: 50px; height: 50px; background-color: #F0FDFA; border-radius: 14px;
  color: teal; font-weight: 700; display: flex; align-items: center; justify-content: center; font-size: 14px;
}
.user-info { display: flex; flex-direction: column; justify-content: center; height: 50px; }
.user-phone { font-size: 14px; font-weight: 700; color: #334155; line-height: 1.2; }
.user-role {
  font-size: 12px; color: #94A3B8; margin-top: 4px; background: #F1F5F9;
  padding: 2px 8px; border-radius: 12px; display: inline-block; width: fit-content;
}

.nav-menu { flex: 1; padding: 20px 10px; overflow: hidden; display: flex; flex-direction: column; }
.nav-header { flex-shrink: 0; }

.new-conversation-btn {
  width: 100%; padding: 12px; background: teal; color: white; border: none; border-radius: 10px;
  font-weight: 600; font-size: 14px; cursor: pointer; display: flex; align-items: center;
  justify-content: center; gap: 8px; box-shadow: 0 6px 16px rgba(0, 128, 128, 0.2);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); margin-bottom: 24px;
}
.new-conversation-btn:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0, 128, 128, 0.3); }

.nav-item {
  width: 100%; display: flex; align-items: center; gap: 12px; padding: 10px 14px;
  background: transparent; border: none; border-radius: 10px; cursor: pointer; color: #64748B;
  transition: all 0.2s; margin-bottom: 4px; font-size: 14px; font-weight: 500;
  padding: 10px 0 10px 60px;
}
.nav-item:hover { background-color: #F8FAFC; color: #334155; }
.nav-item.active { background-color: #F0FDFA; color: teal; font-weight: 700; }

.nav-divider { height: 1px; background: #F1F5F9; margin: 16px 0; }
.nav-section-title {
  font-size: 12px; color: #94A3B8; font-weight: 600; text-transform: uppercase;
  letter-spacing: 1px; margin-bottom: 12px; padding-left: 8px;
}

.history-container { flex: 1; overflow-y: auto; min-height: 0; }
.history-item {
  padding: 10px 8px; font-size: 14px; color: #475569; font-weight: 500;
  border-radius: 8px; cursor: pointer; display: flex; flex-direction: column;
  gap: 4px; margin-bottom: 4px; transition: all 0.2s;
}
.history-item:hover { background-color: #F8FAFC; color: #334155; }
.history-item.active { background-color: #fff; color: teal; font-weight: 600; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03); border: 1px solid #F1F5F9; }

.history-content-wrapper { display: flex; flex-direction: column; gap: 2px; width: 100%; overflow: hidden; }
.history-title { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; width: 100%; }
.history-time { font-size: 11px; color: #94A3B8; font-weight: normal; }
.empty-history { font-size: 13px; color: #CBD5E1; text-align: center; margin-top: 20px; }

.context-menu {
  position: fixed; z-index: 9999; background: white; border: 1px solid #E2E8F0;
  border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); padding: 6px;
  min-width: 140px; display: flex; flex-direction: column; gap: 2px;
}
.menu-item {
  padding: 8px 12px; font-size: 13px; color: #334155; border-radius: 6px;
  cursor: pointer; display: flex; align-items: center; gap: 8px; transition: background 0.1s;
}
.menu-item:hover { background-color: #F1F5F9; }
.menu-item.delete { color: #EF4444; }
.menu-item.delete:hover { background-color: #FEF2F2; }

/* === 主内容区 === */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 24px 36px;
  overflow: hidden;
  overflow-x: hidden; /* 强制屏蔽横向滚动 */
  overflow-y: hidden; /* 强制屏蔽纵向滚动 */
}
.top-bar { margin-bottom: 24px; }
.greeting { font-size: 22px; font-weight: 800; color: #1E293B; letter-spacing: -0.5px; }

/* === 新版报告头部 (左右布局) === */
.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.header-left { display: flex; flex-direction: column; gap: 4px; }
.result-title { font-size: 24px; font-weight: 800; color: #1E293B; margin: 0; }
.result-meta { font-size: 13px; color: #94A3B8; margin: 0; }

/* === 现代仪表盘风格评分 === */
.score-display {
  display: flex;
  flex-direction: column;
  align-items: flex-end; /* 右对齐 */
  justify-content: center;
}
.score-main {
  line-height: 1;
  margin-bottom: 6px;
}
.score-value {
  font-size: 48px;
  font-weight: 800;
  color: teal;
  letter-spacing: -1px;
}
.score-unit {
  font-size: 16px;
  color: #64748B;
  font-weight: 600;
  margin-left: 4px;
}
.score-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
}
.rating-high { background-color: #ECFDF5; color: #059669; }
.rating-good { background-color: #F0FDFA; color: teal; }
.rating-mid { background-color: #FFFBEB; color: #D97706; }
.rating-low { background-color: #FEF2F2; color: #DC2626; }


.dashboard-wrapper { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
/* 减小间距，防止溢出 */
.dashboard-body { display: flex; height: 100%; gap: 24px; }

/* 允许面板收缩，减小 min-width */
.left-panel {
  flex: 6;
  min-width: 450px;
  flex-shrink: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow-y: auto;
  padding-right: 5px;
}

.dashboard-body:not(:has(.right-panel)) .left-panel {
  flex: 1;
  max-width: 800px;
  margin: 0 auto;
  min-width: 400px;
}
.right-panel {
  flex: 4;
  min-width: 300px;
  flex-shrink: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  padding-bottom: 20px;
  padding-left: 10px;
}

.card {
  background: white; border-radius: 20px; padding: 40px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04); border: 1px solid rgba(255, 255, 255, 0.6);
  display: flex; flex-direction: column;
  width: 100%;
  box-sizing: border-box;
  min-height: 800px;
}

/* === 模式 A: 上传卡片 === */
.video-card { height: 100%; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-shrink: 0; }
.card-header h3 { margin: 0; font-size: 17px; font-weight: 700; color: #1E293B; }
.status-badge { font-size: 12px; color: teal; background: #F0FDFA; padding: 4px 10px; border-radius: 20px; font-weight: 600; }

/* 个人中心卡片样式 */
.card.page-content {
  padding: 40px;
  height: auto;
  min-height: 600px;
}

.video-area {
  flex: 1; background-color: #F8FAFC; border: 2px dashed #CBD5E1; border-radius: 16px;
  overflow: hidden; position: relative; display: flex; align-items: center; justify-content: center;
  transition: all 0.3s ease; min-height: 240px; margin-bottom: 24px;
}
.video-area:hover { border-color: teal; background-color: #F0FDFA; }
.video-area.has-video { background: white; border: none; padding: 16px; }

.video-with-controls {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.reselect-btn {
  background: teal;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  align-self: center;
  box-shadow: 0 4px 12px rgba(0, 128, 128, 0.2);
}

.reselect-btn:hover {
  background: #006666;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 128, 128, 0.3);
}
.real-video { width: 100%; height: 100%; object-fit: contain; }

.upload-placeholder { text-align: center; cursor: pointer; width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.placeholder-img-icon { width: 128px; height: 128px; object-fit: contain; margin-bottom: 20px; opacity: 1; transition: transform 0.3s ease; }
.upload-placeholder:hover .placeholder-img-icon { transform: scale(1.05); }
.upload-title { font-size: 15px; font-weight: 700; color: #334155; margin-bottom: 6px; }
.upload-desc { font-size: 12px; color: #94A3B8; }

.form-area { display: flex; flex-direction: column; gap: 20px; }
.input-group { display: flex; flex-direction: column; gap: 8px; }
.input-group label { font-size: 13px; font-weight: 600; color: #475569; }
.optional { color: #94A3B8; font-weight: normal; font-size: 12px; }
.required { color: #EF4444; font-weight: normal; font-size: 12px; }
.modern-input {
  height: 44px; padding: 0 14px; border: 1px solid #E2E8F0; background: #F8FAFC;
  border-radius: 10px; font-size: 14px; color: #334155; transition: all 0.2s;
}
.modern-input:focus { border-color: teal; background: white; outline: none; box-shadow: 0 0 0 4px rgba(0, 128, 128, 0.1); }
.action-buttons { display: flex; flex-direction: column; gap: 20px; margin-top: 8px; }
.btn-primary {
  height: 36px; background: teal; color: white; border: none; border-radius: 10px;
  font-size: 14px; font-weight: 600; letter-spacing: 0.5px; cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 4px 12px rgba(0, 128, 128, 0.2);
  padding: 0 16px;
}
.btn-primary:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0, 128, 128, 0.3); background: #006666; }
.btn-primary:disabled { background: #CBD5E1; cursor: not-allowed; box-shadow: none; }
.btn-text { background: none; border: none; color: #94A3B8; cursor: pointer; font-size: 13px; font-weight: 500; transition: color 0.2s; }
.btn-text:hover { color: #475569; text-decoration: underline; }

/* === 模式 B: 报告模式左侧堆栈 === */
.result-left-stack { display: flex; flex-direction: column; gap: 24px; }

.result-right-stack { display: flex; flex-direction: column; gap: 15px; height: 100%; overflow-y: auto; }

.summary-card { padding: 20px; min-height: auto; margin-bottom: 15px; }
.summary-card h4 { margin: 0 0 12px 0; font-size: 16px; font-weight: 700; }
.danger-card h4 { color: #EF4444; }
.suggest-card h4 { color: #3B82F6; }
.summary-card ul { padding-left: 20px; margin: 0; font-size: 14px; color: #475569; line-height: 1.6; }


/* === 右侧结果面板 === */
.state-card {
  background: white; border-radius: 20px; height: 100%; display: flex; flex-direction: column;
  align-items: center; justify-content: center; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04);
  text-align: center; border: 1px solid rgba(255, 255, 255, 0.6);
}
.placeholder-illustration { width: 260px; max-width: 80%; height: auto; object-fit: contain; margin-bottom: 28px; filter: drop-shadow(0 10px 20px rgba(0, 128, 128, 0.08)); }
.empty-state h3 { font-size: 20px; font-weight: 700; color: #1E293B; margin-bottom: 14px; }
.empty-state p { font-size: 14px; line-height: 1.8; color: #64748B; max-width: 320px; }

/* 报告时间轴卡片 */
.timeline-card { height: 100%; padding: 0; display: flex; flex-direction: column; }
.timeline-header { padding: 24px 28px; border-bottom: 1px solid #F1F5F9; margin: 0; display: flex; justify-content: space-between; align-items: center; flex-shrink: 0; }
.step-count { font-size: 13px; color: #94A3B8; font-weight: 600; background: #F8FAFC; padding: 4px 10px; border-radius: 12px; }

.section-title { font-size: 16px; color: #1E293B; margin: 0; padding-left: 10px; border-left: 4px solid teal; font-weight: 700; }

.step-timeline { flex: 1; padding: 28px; background: #fff; }
.timeline-item { display: flex; gap: 20px; padding-bottom: 32px; position: relative; }
.timeline-item:last-child { padding-bottom: 0; }
.timeline-marker {
  width: 16px; height: 16px; border-radius: 50%; background: #CBD5E1; position: relative;
  top: 6px; z-index: 2; border: 3px solid white; box-shadow: 0 0 0 2px #E2E8F0;
}
.timeline-item::before { content: ''; position: absolute; left: 7px; top: 22px; bottom: 0; width: 2px; background: #E2E8F0; z-index: 1; }
.timeline-item:last-child::before { display: none; }
.timeline-item.success .timeline-marker { background: #2ecc71; box-shadow: 0 0 0 2px #DCFCE7; }
.timeline-item.error .timeline-marker { background: #e74c3c; box-shadow: 0 0 0 2px #FEE2E2; }
.timeline-content { flex: 1; background: #F8FAFC; padding: 16px 20px; border-radius: 12px; border: 1px solid #F1F5F9; }
.step-head { display: flex; justify-content: space-between; margin-bottom: 8px; }
.step-head strong { font-size: 15px; color: #334155; }
.tag { font-size: 12px; padding: 4px 10px; border-radius: 6px; font-weight: 600; }
.tag.success { color: #15803d; background: #dcfce7; }
.tag.error { color: #b91c1c; background: #fee2e2; }
.tag.warning { color: #b45309; background: #fef3c7; }
.timeline-content p { margin: 0; font-size: 14px; color: #64748B; line-height: 1.6; }

/* === 骨架屏加载态优化 === */
.skeleton-container { position: relative; overflow: hidden; }
.skeleton-block, .skeleton-line, .skeleton-marker { background: #F1F5F9; border-radius: 4px; position: relative; overflow: hidden; }
.skeleton-block::after, .skeleton-line::after, .skeleton-marker::after {
  content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent);
  transform: translateX(-100%); animation: shimmer 1.5s infinite;
}
@keyframes shimmer { 100% { transform: translateX(100%); } }

.title-block { width: 200px; height: 24px; }
.badge-block { width: 60px; height: 24px; border-radius: 12px; }
.skeleton-item { margin-bottom: 32px; }
.skeleton-marker { width: 16px; height: 16px; border-radius: 50%; background: #E2E8F0; }
.skeleton-content { background: white; border: 1px solid #F1F5F9; padding: 16px; flex: 1; }
.skeleton-line { height: 16px; margin-bottom: 10px; background: #F1F5F9; }
.skeleton-line:last-child { margin-bottom: 0; }
.width-30 { width: 30%; height: 20px; margin-bottom: 12px; }
.width-80 { width: 80%; }

.loading-overlay {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(2px);
  display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 10;
}
.loading-overlay h3 { font-size: 18px; color: #334155; margin: 20px 0 8px 0; font-weight: 700; }
.loading-subtext { font-size: 13px; color: #64748B; animation: pulse 2s infinite; }
@keyframes pulse { 0% { opacity: 0.6; } 50% { opacity: 1; } 100% { opacity: 0.6; } }

.radar-spinner {
  width: 60px; height: 60px; border-radius: 50%;
  background: conic-gradient(from 0deg, transparent 0%, teal 100%);
  mask: radial-gradient(farthest-side, transparent calc(100% - 4px), #fff 0);
  -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 4px), #fff 0);
  animation: radar-spin 1s linear infinite; position: relative;
}
@keyframes radar-spin { to { transform: rotate(360deg); } }

.function-page { padding: 40px; width: 100%; max-width: 900px; margin: 0 auto; overflow: hidden; }

/* 班级管理页面样式 */
.classes-page {
  width: 100%;
  overflow: hidden;
}

.classes-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #E2E8F0;
}

.classes-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #334155;
}

.classes-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-container {
  position: relative;
}

.search-input {
  height: 36px;
  padding: 0 14px;
  border: 1px solid #E2E8F0;
  background: #F8FAFC;
  border-radius: 10px;
  font-size: 14px;
  color: #334155;
  transition: all 0.2s;
  width: 200px;
}

.search-input:focus {
  border-color: teal;
  background: white;
  outline: none;
  box-shadow: 0 0 0 4px rgba(0, 128, 128, 0.1);
  width: 250px;
}

.classes-content {
  width: 100%;
}

.classes-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 600px;
  overflow-y: auto;
  padding-right: 8px;
}

.class-detail {
  width: 100%;
}

.class-detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #E2E8F0;
  justify-content: space-between;
}

.class-detail-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.student-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.form-hint {
  font-size: 12px;
  color: #94A3B8;
  margin-top: 8px;
  white-space: pre-line;
}

/* 考试系统样式 */
.exams-page {
  width: 100%;
  overflow: hidden;
}

.exams-header {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #E2E8F0;
}

.exams-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #334155;
}

.exams-content {
  width: 100%;
}

.exams-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 600px;
  overflow-y: auto;
  padding-right: 8px;
}

.exam-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px;
  background: #F8FAFC;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
  transition: all 0.2s;
}

.exam-item:hover {
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.exam-info {
  flex: 1;
}

.exam-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 700;
  color: #334155;
}

.exam-info p {
  margin: 4px 0;
  font-size: 14px;
  color: #64748B;
}

.exam-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.modern-select {
  height: 44px;
  padding: 0 14px;
  border: 1px solid #E2E8F0;
  background: #F8FAFC;
  border-radius: 10px;
  font-size: 14px;
  color: #334155;
  transition: all 0.2s;
  width: 100%;
  box-sizing: border-box;
}

.modern-select:focus {
  border-color: teal;
  background: white;
  outline: none;
  box-shadow: 0 0 0 4px rgba(0, 128, 128, 0.1);
}

.class-detail-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #334155;
}

.class-detail-content {
  width: 100%;
}

.function-content {
  width: 100%;
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.page-header { display: flex; align-items: center; gap: 16px; margin-bottom: 32px; }
.back-link { background: none; border: none; font-size: 15px; color: teal; cursor: pointer; font-weight: 600; }
.page-content { height: 500px; display: flex; flex-direction: column; }
.placeholder-content { text-align: center; color: #CBD5E1; }
.center-content { align-items: center; display: flex; flex-direction: column; justify-content: center; }
.profile-large-avatar { width: 96px; height: 96px; background: #F1F5F9; border-radius: 24px; margin-bottom: 24px; }
.role-tag { background: #F1F5F9; padding: 6px 16px; border-radius: 20px; font-size: 13px; margin-top: 12px; color: #64748B; font-weight: 500; }
.logout-btn { margin-top: 48px; padding: 12px 48px; border: 1px solid #EF4444; color: #EF4444; background: white; border-radius: 12px; cursor: pointer; transition: all 0.2s; font-weight: 600; }
.logout-btn:hover { background: #FEF2F2; }

/* 个人中心样式 */
.profile-tabs {
  display: flex;
  border-bottom: 1px solid #e8e8e8;
  margin-bottom: 40px;
}

.tab-btn {
  padding: 18px 28px;
  background: none;
  border: none;
  font-size: 18px;
  color: #666;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
}

.tab-btn:hover {
  color: #1890FF;
}

.tab-btn.active {
  color: #1890FF;
  border-bottom-color: #1890FF;
  font-weight: 600;
}

.profile-content {
  padding: 40px 0;
  width: 100%;
}

.profile-item {
  margin-bottom: 36px;
  padding-bottom: 28px;
  border-bottom: 1px solid #f0f0f0;
  width: 100%;
}

.profile-row {
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  width: 100%;
}

.profile-label {
  width: 120px;
  font-size: 18px;
  color: #666;
  font-weight: 500;
  white-space: nowrap;
  margin-right: 20px;
}

.profile-value {
  flex: 1;
  font-size: 18px;
  color: #333;
  display: flex;
  align-items: center;
  gap: 20px;
  white-space: nowrap;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-right: 40px;
  cursor: pointer;
  font-size: 18px;
}

.radio-label input[type="radio"] {
  margin: 0;
  width: 20px;
  height: 20px;
}

.edit-btn, .add-btn {
  background: none;
  border: none;
  color: #1890FF;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
}

.edit-btn:hover, .add-btn:hover {
  text-decoration: underline;
}

.unit-info {
  flex-direction: column;
  align-items: flex-start;
  gap: 12px;
}

.unit-id {
  font-size: 16px;
  color: #999;
}

.profile-actions {
  margin-top: 50px;
  display: flex;
  justify-content: center;
}

.logout-btn {
  padding: 16px 64px;
  font-size: 18px;
}

/* 个人中心响应式设计 */
@media (max-width: 768px) {
  .profile-tabs {
    flex-wrap: wrap;
  }
  
  .tab-btn {
    padding: 8px 12px;
    font-size: 12px;
  }
  
  .profile-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .profile-label {
    width: 100%;
  }
  
  .profile-value {
    width: 100%;
  }
}

.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(8px); z-index: 2000;
  display: flex; justify-content: center; align-items: center;
}

/* 班级管理样式 */
.class-header-section {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  width: 100%;
  box-sizing: border-box;
  padding: 0 28px;
  margin-left: -28px;
  margin-right: -28px;
}

/* 确保父容器没有额外的边距 */
.card.page-content > div > div {
  margin: 0;
  padding: 0;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  box-sizing: border-box;
}

/* 确保班级列表也居左显示并与分割线宽度匹配 */
.class-list-section {
  width: 100%;
  box-sizing: border-box;
}

.class-header-section .btn-primary {
  align-self: flex-start;
  margin: 0;
  padding: 0 16px;
  height: 36px;
}

.class-content-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  padding: 0 28px;
  margin-left: -28px;
  margin-right: -28px;
}

.divider {
  height: 1px;
  background-color: #E2E8F0;
  margin-top: 15px;
  margin-bottom: 20px;
  width: 100%;
  box-sizing: border-box;
}

/* 教师模式下的分割线 */
.app-container.teacher-mode .divider {
  background-color: #E2E8F0;
}

.class-create-section,
.class-join-section {
  margin-bottom: 20px;
  padding-bottom: 0;
  border-bottom: none;
  width: 100%;
}

.class-create-section h3,
.class-join-section h3,
.class-list-section h3 {
  margin-bottom: 20px;
  font-size: 18px;
  font-weight: 900;
  color: #334155;
}

.form-group {
  margin-bottom: 20px;
  width: 100%;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #475569;
}

.modern-input {
  width: 100%;
  box-sizing: border-box;
}

.modern-textarea {
  width: 100%;
  max-width: 100%;
  min-height: 100px;
  padding: 12px 14px;
  border: 1px solid #E2E8F0;
  background: #F8FAFC;
  border-radius: 10px;
  font-size: 14px;
  color: #334155;
  resize: vertical;
  transition: all 0.2s;
  box-sizing: border-box;
}

.modern-textarea:focus {
  border-color: teal;
  background: white;
  outline: none;
  box-shadow: 0 0 0 4px rgba(0, 128, 128, 0.1);
}

.class-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 600px;
  overflow-y: auto;
  padding-right: 8px;
}

.class-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px;
  background: #F8FAFC;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
  transition: all 0.2s;
  cursor: pointer;
  width: 100%;
  box-sizing: border-box;
}

.class-item:hover {
  background: #F0FDFA;
  border-color: #CBD5E1;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.class-info h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 700;
  color: #1E293B;
}

.class-info p {
  margin: 4px 0;
  font-size: 14px;
  color: #64748B;
}

.class-actions {
  display: flex;
  gap: 10px;
}

.delete-btn {
  color: #EF4444;
}

.delete-btn:hover {
  color: #DC2626;
  text-decoration: underline;
}

/* 弹窗样式 */
.modal-content {
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
}

.class-detail-modal {
  max-width: 700px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #F1F5F9;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #1E293B;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #94A3B8;
  cursor: pointer;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #F1F5F9;
  color: #334155;
}

.modal-body {
  padding: 24px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 24px;
  border-top: 1px solid #F1F5F9;
}

/* 学生列表样式 */
.student-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 500px;
  overflow-y: auto;
  padding-right: 8px;
}

.student-item {
  padding: 16px;
  background: #F8FAFC;
  border-radius: 10px;
  border: 1px solid #E2E8F0;
  transition: all 0.2s;
}

.student-item:hover {
  background: #F0FDFA;
  border-color: #CBD5E1;
}

.student-info p {
  margin: 4px 0;
  font-size: 14px;
  color: #64748B;
}

/* 教师模式下的班级管理样式 */
.app-container.teacher-mode .class-header h3 {
  color: #1890FF;
}

.app-container.teacher-mode .class-create-section h3,
.app-container.teacher-mode .class-join-section h3,
.app-container.teacher-mode .class-list-section h3 {
  color: #1890FF;
}

.app-container.teacher-mode .form-group label {
  color: #1890FF;
}

.app-container.teacher-mode .class-item {
  background: #E6F7FF;
  border-color: #91D5FF;
}

.app-container.teacher-mode .class-item:hover {
  background: #BAE7FF;
  border-color: #1890FF;
}

.app-container.teacher-mode .class-info h4 {
  color: #1890FF;
}

.app-container.teacher-mode .class-info p {
  color: #40A9FF;
}

.app-container.teacher-mode .student-item {
  background: #E6F7FF;
  border-color: #91D5FF;
}

.app-container.teacher-mode .student-item:hover {
  background: #BAE7FF;
  border-color: #1890FF;
}

.app-container.teacher-mode .student-info p {
  color: #40A9FF;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
  color: #94A3B8;
  background: transparent;
  border: none;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 400px;
}

@media (max-width: 1024px) {
  .left-panel, .right-panel { flex: 100%; min-width: 0; }
  .dashboard-body { flex-direction: column; height: 100%; overflow: hidden; }
  .main-content { padding: 20px; overflow: hidden; }
  
  .class-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .class-item {
    flex-direction: column;
    gap: 16px;
  }
  
  .class-actions {
    align-self: flex-start;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
}

/* 教师模式下的textarea样式 */
.app-container.teacher-mode .modern-textarea {
  border-color: #91D5FF;
  background: #E6F7FF;
}

.app-container.teacher-mode .modern-textarea:focus {
  border-color: #1890FF;
  box-shadow: 0 0 0 4px rgba(24, 144, 255, 0.1);
}
</style>