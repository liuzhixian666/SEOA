<template>
  <!-- ==================== 主应用容器 ==================== -->
  <div class="app-container teacher-mode" @click="hideContextMenu">

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
      <div class="sidebar-logo">
        <div class="logo-icon">🧪</div>
        <h1 class="logo-text">SEOA 评估系统</h1>
      </div>

      <!-- 用户信息区域 -->
      <div class="user-profile-area" @click="isLoggedIn ? showMy() : showProfile = true">
        <div class="user-avatar">
          <span v-if="isLoggedIn">User</span>
          <span v-else>未登录</span>
        </div>
        <div class="user-info" v-if="isLoggedIn">
          <span class="user-phone">{{ maskedPhone }}</span>
          <span class="user-role">教师账号</span>
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
             <h1 class="result-title">{{ customExperimentName || '化学实验分析报告' }}</h1>
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

              <!-- 教师端：批量视频上传 -->
              <div class="video-area" :class="{ 'has-videos': selectedFiles.length > 0 }">
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
                    :multiple="true"
                    style="display: none" 
                    @change="handleFileChange" 
                  />
                  <button class="btn-primary" @click="handleMainBtnClick" :disabled="isLoading">
                    {{ isLoading ? 'AI 正在分析...' : (selectedFiles.length > 0 ? '开始批量评估' : '选择视频文件') }}
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
                         <span class="status-icon"></span>
                         <div class="point-info">
                           <div class="point-name">{{ point.point_name || '评分点' }}</div>
                           <div class="point-description">{{ point.point }}</div>
                         </div>
                         <span class="point-score">{{ point.score || 0 }}分</span>
                        <span v-if="point.deduction > 0" class="deduction">(扣{{ point.deduction }}分)</span>
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
        
          <!-- ==================== 管理页面 ==================== -->
          <div v-if="currentFunction === 'classes'" class="classes-page">
            <!-- 教师端：创建班级按钮和班级列表 -->
            <div v-if="!isClassDetailPage">
              <div class="classes-header">
                <h2>我教的课</h2>
                <div class="header-actions">
                  <button class="btn-primary" @click="handleCreateClassClick">
                    + 新建课程
                  </button>
                  <div class="search-box">
                    <input 
                      type="text" 
                      v-model="searchKeyword" 
                      placeholder="搜索课程名称..." 
                      class="search-input"
                      @input="handleSearch"
                    >
                  </div>
                </div>
              </div>
              
              <div class="classes-content">
                <div v-if="filteredTeacherClasses.length > 0" class="classes-list">
                  <div class="course-grid">
                    <div v-for="cls in filteredTeacherClasses" :key="cls.id" class="course-card" @click="enterClassDetail(cls.id)">
                      <div class="course-image">
                        <img :src="evaluate2" alt="课程图片" />
                      </div>
                      <div class="course-info">
                        <h4>{{ cls.class_name }}</h4>
                        <p class="course-code">课程码：{{ cls.class_code }}</p>
                        <p v-if="cls.description" class="course-description">{{ cls.description }}</p>
                        <div class="course-actions">
                          <button class="btn-text" @click.stop="copyClassCode(cls.class_code)">复制课程码</button>
                          <button class="btn-text delete-btn" @click.stop="deleteClass(cls.id)">删除课程</button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else-if="!isLoading" class="empty-state">
                  <p>您还没有创建任何课程</p>
                </div>
              </div>
            </div>
            
            <!-- 班级详情页面（学生列表） -->
            <div v-else class="class-detail">
              <div class="class-detail-header">
                <button class="btn-secondary" @click="backToClassList">
                  <span>&larr;</span>
                  <span>返回班级列表</span>
                </button>
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
          <!-- ==================== 考试系统模块 ==================== -->
          <div v-else-if="currentFunction === 'exams'" class="exams-page">
            <div class="exams-header">
              <div class="tab-buttons">
                <button class="tab-btn" :class="{ 'active': examsTab === 'exams' }" @click="examsTab = 'exams'">考试管理</button>
                <button class="tab-btn" :class="{ 'active': examsTab === 'templates' }" @click="examsTab = 'templates'">评价表模板</button>
              </div>
            </div>
            
            <!-- 考试管理标签页 -->
            <div v-if="examsTab === 'exams'" class="exams-content">
              <div class="exams-actions">
                <button class="btn-primary" @click="handleCreateExamClick">发布考试</button>
              </div>
              
              <div v-if="teacherExams.length > 0" class="exams-list">
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
              <div v-else-if="!isLoading" class="empty-state">
                <p>您还没有发布任何考试</p>
              </div>
            </div>
            
            <!-- 评价表模板标签页 -->
            <div v-if="examsTab === 'templates'" class="templates-content">
              <div class="templates-actions">
                <button class="btn-primary" @click="handleCreateTemplateClick">创建模板</button>
              </div>
              
              <!-- 模板详情页面 -->
              <div v-if="showTemplateDetail" class="template-detail-page">
                <div class="detail-header">
                  <button class="btn-secondary" @click="showTemplateDetail = false">
                    <span>&larr;</span>
                    <span>返回</span>
                  </button>
                  <h3>{{ selectedTemplate?.template_name }} {{ selectedTemplate?.is_default ? '(系统默认)' : '' }}</h3>
                </div>
                <div class="template-detail-content">
                  <div class="template-meta">
                    <p><strong>描述：</strong>{{ selectedTemplate?.description || '无描述' }}</p>
                    <p><strong>创建时间：</strong>{{ selectedTemplate?.created_at ? formatTime(selectedTemplate.created_at) : '未知' }}</p>
                  </div>
                  <div class="template-steps">
                    <h4>评价步骤</h4>
                    <div v-for="(step, stepIndex) in selectedTemplate?.steps" :key="step.id" class="template-step">
                      <h5>{{ step.step_name || step.name }}</h5>
                      <div class="step-score-points">
                        <div v-for="(point, pointIndex) in step.score_points" :key="point.id" class="score-point">
                          <h4>{{ pointIndex + 1 }}. {{ point.point_name || '评分点' }}</h4>
                          <div class="score-point-details">
                            <p v-if="point.scoring_criteria || point.point || point.criteria || point.standard"><strong>评分标准：</strong>{{ point.scoring_criteria || point.point || point.criteria || point.standard }}</p>
                            <p><strong>分值：</strong>{{ point.score || 0 }}分</p>
                            <p v-if="point.deduction_description"><strong>扣分点说明：</strong>{{ point.deduction_description }}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 模板列表 -->
              <div v-else>
                <div v-if="evaluationTemplates.length > 0" class="templates-list">
                  <div v-for="template in evaluationTemplates" :key="template.id" class="template-item">
                    <div class="template-info">
                      <h4>{{ template.template_name }} {{ template.is_default ? '(系统默认)' : '' }}</h4>
                      <p>{{ template.description }}</p>
                      <p>创建时间：{{ formatTime(template.created_at) }}</p>
                    </div>
                    <div class="template-actions">
                      <button class="btn-text" @click="viewTemplateDetails(template.id)">查看详情</button>
                      <button v-if="!template.is_default" class="btn-text delete-btn" @click="deleteTemplate(template.id)">删除</button>
                    </div>
                  </div>
                </div>
                <div v-else-if="!isLoading" class="empty-state">
                  <p>暂无评价表模板</p>
                </div>
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
                  <div v-if="!notif.is_read" class="unread-indicator"></div>

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
          <div class="profile-tabs">
            <button class="tab-btn active">基本资料</button>
            <button class="tab-btn">修改头像</button>
            <button class="tab-btn">密码管理</button>
            <button class="tab-btn">注销账号</button>
            <button class="tab-btn">语言</button>
          </div>
          
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
                    <label>评分标准</label>
                    <textarea v-model="point.point" class="modern-textarea" placeholder="请输入评分标准"></textarea>
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

<script>
import LoginOrRegister from "./LoginOrRegister.vue";
import request from './utils/request';
import evaluate1 from './assets/evaluate1.png';
import evaluate2 from './assets/evaluate2.png';

export default {
  name: 'TeacherPage',
  components: { LoginOrRegister },
  data() {
    return {
      evaluate1,
      evaluate2,
      isSidebarCollapsed: false,
      isLoggedIn: false,
      showProfile: false,
      showMyPage: false,
      currentFunction: null,
      isLoading: false,
      currentPhone: '',
      userId: '',
      userName: '',
      userGender: 'male',
      userUnit: '',
      userStudentId: '',
      userType: 'teacher',
      historyConversations: [],
      currentConversationId: null,
      selectedVideoURL: null,
      selectedFiles: [],
      reportData: null,
      customExperimentName: '',
      experimentNameError: '',

      functionTitles: {
        messages: '消息中心',
        exams: '考试系统',
        classes: '班级管理'
      },
      teacherClasses: [],
      studentClasses: [],
      filteredTeacherClasses: [],
      showCreateClassModal: false,
      newClassName: '',
      newClassDescription: '',
      joinClassCode: '',
      searchKeyword: '',
      isClassDetailPage: false,
      selectedClass: null,
      classMembers: [],
      showAddStudentModal: false,
      newStudentId: '',
      showImportStudentsModal: false,
      importStudentsText: '',
      teacherExams: [],
      studentExams: [],
      showCreateExamModal: false,
      examsTab: 'exams',
      showTemplateDetail: false,
      selectedTemplate: null,
      showCreateTemplateModal: false,
      newExam: {
        exam_name: '',
        description: '',
        class_id: '',
        template_id: '',
        start_time: '',
        end_time: ''
      },
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
      contextMenu: {
        visible: false,
        x: 0,
        y: 0,
        targetItem: null
      },
      notifications: [],
      unreadCount: 0,
      isLoadingNotifications: false,
      currentPage: 1,
      totalPages: 1,
      unreadTimer: null
    };
  },
  computed: {
    maskedPhone() {
      if (!this.currentPhone) return '';
      if (this.currentPhone.length !== 11) return this.currentPhone;
      return this.currentPhone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
    }
  },
  async created() {
    const token = localStorage.getItem('token');
    if (token) {
      this.isLoggedIn = true;
      this.showProfile = false;
      try {
        await this.loadUserInfo();
        await this.loadHistoryList();
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
    this.stopUnreadPolling();
  },
  methods: {
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
    async handleLoginSuccess() {
      this.showProfile = false;
      this.isLoggedIn = true;
      this.currentPhone = localStorage.getItem('userPhone');
      this.userType = localStorage.getItem('userType') || 'teacher';
      this.userId = localStorage.getItem('userId');
      await this.loadHistoryList();
      this.startUnreadPolling();
    },
    
    async loadUserInfo() {
      if (!this.isLoggedIn) return;
      try {
        const response = await request.get('users/me');
        this.userId = response.user_id;
        this.userName = response.name;
        this.currentPhone = response.user_phone;
        this.userType = response.user_type;
        localStorage.setItem('userId', response.user_id);
        localStorage.setItem('userPhone', response.user_phone);
        localStorage.setItem('userType', response.user_type);
      } catch (error) {
        console.error('加载用户信息失败:', error);
      }
    },
    toggleSidebar() { this.isSidebarCollapsed = !this.isSidebarCollapsed; },
    
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
      if (!this.checkLoginStatus()) return;

      this.currentFunction = func;
      this.showMyPage = false;
      if (func === 'classes') {
        this.loadClassList();
      }
      if (func === 'exams') {
        this.loadExamList();
        this.loadClassList();
        this.loadEvaluationTemplates();
      }
      if (func === 'messages') {
        this.loadNotifications();
        this.loadUnreadCount();
      }
    },
    async showMy() { 
      if (!this.checkLoginStatus()) return;
      
      this.showMyPage = true; 
      this.currentFunction = null; 
      await this.loadUserInfo();
    },
    
    async loadClassList() {
      if (!this.isLoggedIn) return;
      try {
        this.teacherClasses = await request.get('classes');
        this.filteredTeacherClasses = this.teacherClasses;
      } catch (error) {
        console.error('加载班级列表失败:', error);
      }
    },
    
    handleCreateClassClick() {
      if (!this.isLoggedIn) {
        this.showProfile = true;
        return;
      }
      this.showCreateClassModal = true;
    },
    
    async createClass() {
      if (!this.isLoggedIn) {
        this.showProfile = true;
        return;
      }
      if (!this.newClassName.trim()) return;
      try {
        this.isLoading = true;
        await request.post('classes', { 
          class_name: this.newClassName,
          description: this.newClassDescription
        });
        this.newClassName = '';
        this.newClassDescription = '';
        this.showCreateClassModal = false;
        await this.loadClassList();
      } catch (error) {
        console.error('创建班级失败:', error);
      } finally {
        this.isLoading = false;
      }
    },
    
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
    
    backToClassList() {
      this.isClassDetailPage = false;
      this.selectedClass = null;
      this.classMembers = [];
    },
    
    async removeStudent(studentId) {
      if (!this.isLoggedIn) {
        this.showProfile = true;
        return;
      }
      if (confirm('确定要移除这个学生吗？')) {
        try {
          this.isLoading = true;
          await request.delete(`classes/${this.selectedClass.id}/students/${studentId}`);
          await this.enterClassDetail(this.selectedClass.id);
        } catch (error) {
          console.error('删除学生失败:', error);
          alert('删除学生失败，请重试');
        } finally {
          this.isLoading = false;
        }
      }
    },
    
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
    
    handleSearch() {
      if (!this.searchKeyword) {
        this.filteredTeacherClasses = this.teacherClasses;
      } else {
        const keyword = this.searchKeyword.toLowerCase();
        this.filteredTeacherClasses = this.teacherClasses.filter(cls => 
          cls.class_name.toLowerCase().includes(keyword)
        );
      }
    },
    
    copyClassCode(classCode) {
      navigator.clipboard.writeText(classCode).then(() => {
      }).catch(err => {
        console.error('复制失败:', err);
      });
    },
    
    async deleteClass(classId) {
      if (!this.isLoggedIn) {
        this.showProfile = true;
        return;
      }
      if (confirm('确定要解散这个班级吗？解散后班级内的所有学生将自动退出班级。')) {
        try {
          this.isLoading = true;
          await request.delete(`classes/${classId}`);
          await this.loadClassList();
        } catch (error) {
          console.error('解散班级失败:', error);
        } finally {
          this.isLoading = false;
        }
      }
    },
    
    async loadExamList() {
      if (!this.isLoggedIn) return;
      try {
        this.teacherExams = await request.get('exams');
      } catch (error) {
        console.error('加载考试列表失败:', error);
      }
    },
    
    async loadEvaluationTemplates() {
      if (!this.isLoggedIn) return;
      try {
        this.evaluationTemplates = await request.get('templates');
      } catch (error) {
        console.error('加载评价表模板失败:', error);
      }
    },
    
    async handleCreateExamClick() {
      if (!this.isLoggedIn) {
        this.showProfile = true;
        return;
      }
      try {
        await this.loadClassList();
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
        await request.post('exams', {
          exam_name: this.newExam.exam_name,
          description: this.newExam.description,
          class_id: parseInt(this.newExam.class_id),
          template_id: this.newExam.template_id ? parseInt(this.newExam.template_id) : null,
          start_time: this.newExam.start_time,
          end_time: this.newExam.end_time
        });
        await this.loadExamList();
        this.newExam = {
          exam_name: '',
          description: '',
          class_id: '',
          template_id: '',
          start_time: '',
          end_time: ''
        };
        this.showCreateExamModal = false;
        alert('考试发布成功！');
      } catch (error) {
        console.error('发布考试失败:', error);
        alert(`发布考试失败: ${error.response?.data?.detail || '未知错误'}`);
      } finally {
        this.isLoading = false;
      }
    },
    
    async viewExamDetails(examId) {
      try {
        this.isLoading = true;
        const response = await request.get(`exams/${examId}`);
        alert(`考试详情：${response.exam_name}\n${response.description}`);
      } catch (error) {
        console.error('获取考试详情失败:', error);
        alert('获取考试详情失败，请重试');
      } finally {
        this.isLoading = false;
      }
    },
    
    async deleteExam(examId) {
      if (!this.isLoggedIn) {
        this.showProfile = true;
        return;
      }
      if (confirm('确定要删除这个考试吗？')) {
        try {
          this.isLoading = true;
          await request.delete(`exams/${examId}`);
          await this.loadExamList();
        } catch (error) {
          console.error('删除考试失败:', error);
          alert('删除考试失败，请重试');
        } finally {
          this.isLoading = false;
        }
      }
    },
    
    handleCreateTemplateClick() {
      if (!this.isLoggedIn) {
        this.showProfile = true;
        return;
      }
      this.newTemplate = {
        template_name: '',
        description: '',
        steps: [{
          step_name: '',
          score_points: [{
            point_name: '',
            score: 0,
            point: '',
            deduction_description: ''
          }]
        }]
      };
      this.showCreateTemplateModal = true;
    },
    
    addStep() {
      this.newTemplate.steps.push({
        step_name: '',
        score_points: [{
          point_name: '',
          score: 0,
          point: '',
          deduction_description: ''
        }]
      });
    },
    
    removeStep(stepIndex) {
      if (this.newTemplate.steps.length > 1) {
        this.newTemplate.steps.splice(stepIndex, 1);
      }
    },
    
    addScorePoint(stepIndex) {
      this.newTemplate.steps[stepIndex].score_points.push({
        point_name: '',
        score: 0,
        point: '',
        deduction_description: ''
      });
    },
    
    removeScorePoint(stepIndex, pointIndex) {
      if (this.newTemplate.steps[stepIndex].score_points.length > 1) {
        this.newTemplate.steps[stepIndex].score_points.splice(pointIndex, 1);
      }
    },
    
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
        const templateResponse = await request.post('templates', {
          template_name: this.newTemplate.template_name,
          description: this.newTemplate.description
        });
        const templateId = templateResponse.id;
        
        for (let i = 0; i < this.newTemplate.steps.length; i++) {
          const step = this.newTemplate.steps[i];
          if (!step.step_name.trim()) {
            throw new Error(`请填写步骤 ${i + 1} 的名称`);
          }
          
          const stepResponse = await request.post(`templates/${templateId}/steps`, {
            step_name: step.step_name,
            step_order: i + 1
          });
          const stepId = stepResponse.id;
          
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
              scoring_criteria: point.point,
              deduction_description: point.deduction_description
            });
          }
        }
        
        await this.loadEvaluationTemplates();
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
        alert('模板创建成功！');
      } catch (error) {
        console.error('创建模板失败:', error);
        alert(`创建模板失败: ${error.message || '未知错误'}`);
      } finally {
        this.isLoading = false;
      }
    },
    
    async viewTemplateDetails(templateId) {
      try {
        this.isLoading = true;
        const response = await request.get(`templates/${templateId}`);
        this.selectedTemplate = response;
        this.showTemplateDetail = true;
      } catch (error) {
        console.error('获取模板详情失败:', error);
        alert('获取模板详情失败，请重试');
      } finally {
        this.isLoading = false;
      }
    },
    
    async deleteTemplate(templateId) {
      if (!this.isLoggedIn) {
        this.showProfile = true;
        return;
      }
      if (confirm('确定要删除这个模板吗？')) {
        try {
          this.isLoading = true;
          await request.delete(`templates/${templateId}`);
          await this.loadEvaluationTemplates();
        } catch (error) {
          console.error('删除模板失败:', error);
          alert('删除模板失败，请重试');
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
      this.selectedFiles = Array.from(files);
    },
    
    removeFile(index) {
      this.selectedFiles.splice(index, 1);
    },
    
    handleMainBtnClick() {
      if (!this.checkLoginStatus()) return;
      
      if (this.selectedFiles.length === 0) {
        this.$refs.videoInput.click();
      } else {
        if (!this.customExperimentName || this.customExperimentName.trim() === '') {
          this.experimentNameError = '请输入实验名称';
          return;
        }
        this.experimentNameError = '';
        this.startBatchAnalysis();
      }
    },
    async startBatchAnalysis() {
      if (!this.checkLoginStatus()) return;
      
      if (this.selectedFiles.length === 0) return;
      
      this.isLoading = true;
      this.reportData = null;
      
      try {
        for (let i = 0; i < this.selectedFiles.length; i++) {
          const file = this.selectedFiles[i];
          const title = `${this.customExperimentName} - ${file.name}`;
          
          const conv = await request.post('conversations', {title: title});
          const convId = conv.id;
          
          const formData = new FormData();
          formData.append('video', file);
          if (this.customExperimentName) { formData.append('experiment_name', this.customExperimentName); }
          
          await request.post(`conversations/${convId}/video`, formData, {
            headers: {'Content-Type': 'multipart/form-data'},
            timeout: 120000
          });
        }
        
        await this.loadHistoryList();
        alert(`已成功提交 ${this.selectedFiles.length} 个视频进行分析`);
        this.resetSelection();
        
      } catch (error) {
        alert('批量分析失败，请检查网络或文件大小');
        console.error(error);
      } finally {
        this.isLoading = false;
      }
    },
    async loadHistory(id) {
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

          const currentItem = this.historyConversations.find(item => item.id === id);
          if (this.reportData && currentItem) {
            this.reportData.create_time = currentItem.updated_at;
          } else if (this.reportData) {
            this.reportData.create_time = new Date();
          }

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
    getScoreRating(score) {
      if (score >= 90) return '优秀';
      if (score >= 80) return '良好';
      if (score >= 60) return '及格';
      return '需改进';
    },
    getScoreRatingClass(score) {
      if (score >= 90) return 'rating-high';
      if (score >= 80) return 'rating-good';
      if (score >= 60) return 'rating-mid';
      return 'rating-low';
    },
    getScoreClass(score) {
      if (score >= 90) return 'score-high';
      if (score >= 60) return 'score-mid';
      return 'score-low';
    },

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
    
    async loadUnreadCount() {
      if (!this.isLoggedIn) return;
      try {
        const response = await request.get('notifications/unread-count');
        this.unreadCount = response.unread_count || 0;
      } catch (error) {
        console.error('获取未读数失败:', error);
      }
    },
    
    async markAsRead(notificationId) {
      try {
        await request.put(`notifications/${notificationId}/read`);
        const notif = this.notifications.find(n => n.id === notificationId);
        if (notif) {
          notif.is_read = true;
          this.unreadCount = Math.max(0, this.unreadCount - 1);
        }
      } catch (error) {
        console.error('标记已读失败:', error);
      }
    },
    
    async markAllAsRead() {
      try {
        await request.put('notifications/read-all');
        this.notifications.forEach(n => n.is_read = true);
        this.unreadCount = 0;
      } catch (error) {
        console.error('全部标记已读失败:', error);
      }
    },
    
    async viewNotification(notification) {
      if (!notification.is_read) {
        await this.markAsRead(notification.id);
      }
      
      if (notification.notification_type === 'exam_announcement' && notification.related_id) {
        this.currentFunction = 'exams';
        this.examsTab = 'exams';
        await this.loadExamList();
        await this.viewExamDetails(notification.related_id);
      }
    },
    
    prevPage() {
      if (this.currentPage > 1) {
        this.loadNotifications(this.currentPage - 1);
      }
    },
    
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.loadNotifications(this.currentPage + 1);
      }
    },
    
    startUnreadPolling() {
      this.stopUnreadPolling();
      this.unreadTimer = setInterval(() => {
        if (this.isLoggedIn) {
          this.loadUnreadCount();
        }
      }, 30000);
    },
    
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
html, body {
  margin: 0;
  padding: 0;
  overflow: hidden;
  height: 100%;
  width: 100%;
}
</style>

<style scoped>
.app-container {
  display: flex; height: 100vh; width: 100vw; overflow: hidden;
  background-color: #FFFFFF;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  color: #334155;
  transition: all 0.3s ease;
}

.app-container.teacher-mode { background-color: #FFFFFF; color: #1890FF; }
.app-container.teacher-mode .sidebar { background-color: #FFFFFF; box-shadow: 4px 0 24px rgba(24, 144, 255, 0.1); }
.app-container.teacher-mode .logo-text { color: #1890FF; }
.app-container.teacher-mode .user-avatar { background-color: #E6F7FF; color: #1890FF; }
.app-container.teacher-mode .new-conversation-btn { background: #1890FF; box-shadow: 0 6px 16px rgba(24, 144, 255, 0.2); }
.app-container.teacher-mode .new-conversation-btn:hover { box-shadow: 0 10px 20px rgba(24, 144, 255, 0.3); }
.app-container.teacher-mode .nav-item.active { background-color: #E6F7FF; color: #1890FF; }
.app-container.teacher-mode .nav-item:hover { background-color: #F0F9FF; color: #1890FF; }
.app-container.teacher-mode .btn-primary { background: #1890FF; box-shadow: 0 4px 12px rgba(24, 144, 255, 0.2); }
.app-container.teacher-mode .btn-primary:hover:not(:disabled) { background: #40A9FF; box-shadow: 0 8px 20px rgba(24, 144, 255, 0.3); }
.app-container.teacher-mode .score-value { color: #1890FF; }
.app-container.teacher-mode .section-title { border-left: 4px solid #1890FF; }
.app-container.teacher-mode .reselect-btn { background: #1890FF; box-shadow: 0 4px 12px rgba(24, 144, 255, 0.2); }
.app-container.teacher-mode .reselect-btn:hover { background: #40A9FF; box-shadow: 0 8px 20px rgba(24, 144, 255, 0.3); }
.app-container.teacher-mode .video-area { background-color: #E6F7FF; border-color: #91D5FF; }
.app-container.teacher-mode .video-area:hover { border-color: #1890FF; background-color: #BAE7FF; }
.app-container.teacher-mode .video-area.has-video { background: white; }
.app-container.teacher-mode .video-area.has-videos { background: white; }
.app-container.teacher-mode .batch-upload-container h4 { color: #1890FF; }
.app-container.teacher-mode .file-list li { background: #E6F7FF; border-color: #91D5FF; }
.app-container.teacher-mode .remove-file-btn:hover { background: #FFF1F0; }
.app-container.teacher-mode .card-header h3 { color: #1890FF; }
.app-container.teacher-mode .status-badge { color: #1890FF; background: #E6F7FF; }
.app-container.teacher-mode .input-group label { color: #1890FF; }
.app-container.teacher-mode .modern-input { border-color: #91D5FF; background: #E6F7FF; }
.app-container.teacher-mode .modern-input:focus { border-color: #1890FF; box-shadow: 0 0 0 4px rgba(24, 144, 255, 0.1); }
.app-container.teacher-mode .btn-text { color: #1890FF; }
.app-container.teacher-mode .btn-text:hover { color: #40A9FF; }
.app-container.teacher-mode .result-title { color: #1890FF; }
.app-container.teacher-mode .result-meta { color: #69C0FF; }
.app-container.teacher-mode .step-count { color: #69C0FF; background: #E6F7FF; }
.app-container.teacher-mode .timeline-content { background: #E6F7FF; border-color: #91D5FF; }
.app-container.teacher-mode .step-head strong { color: #1890FF; }
.app-container.teacher-mode .timeline-content p { color: #40A9FF; }

.sidebar {
  width: 260px; background-color: #fff; display: flex; flex-direction: column;
  transition: transform 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94), opacity 0.3s ease, width 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  z-index: 20;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.02); border-right: none;
  position: relative;
  overflow: hidden;
  transform-origin: left;
  flex-shrink: 0;
}
.sidebar.collapsed {
  transform: scaleX(0);
  opacity: 0;
  width: 0;
}

.sidebar-toggle-btn {
  position: absolute; top: 24px; left: 240px; width: 32px; height: 32px;
  background-color: #fff; border: 1px solid #E2E8F0; border-radius: 50%;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); z-index: 1000; color: #64748B;
  transition: left 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94), transform 0.3s ease, box-shadow 0.3s ease, color 0.3s ease;
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

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 24px 36px;
  overflow: hidden;
  overflow-x: hidden;
  overflow-y: hidden;
}

.function-page { padding: 40px; width: 100%; max-width: 1000px; margin: 0 auto; overflow: hidden; }

.top-bar { margin-bottom: 24px; }
.greeting { font-size: 22px; font-weight: 800; color: #1E293B; letter-spacing: -0.5px; }

.result-header { display: flex; justify-content: space-between; align-items: center; }
.header-left { flex: 1; }
.result-title { font-size: 28px; font-weight: 800; color: #1E293B; margin: 0 0 8px 0; letter-spacing: -0.5px; }
.result-meta { font-size: 14px; color: #64748B; margin: 0; }
.header-right { display: flex; align-items: center; gap: 20px; }

.score-display { display: flex; flex-direction: column; align-items: flex-end; justify-content: center; }
.score-main { line-height: 1; margin-bottom: 6px; }
.score-value { font-size: 48px; font-weight: 800; color: teal; letter-spacing: -1px; }
.score-unit { font-size: 16px; color: #64748B; font-weight: 600; margin-left: 4px; }
.score-badge {
  padding: 4px 12px; border-radius: 12px; font-size: 13px; font-weight: 600;
  display: inline-block;
}
.rating-high { background-color: #ECFDF5; color: #059669; }
.rating-good { background-color: #F0FDFA; color: teal; }
.rating-mid { background-color: #FFFBEB; color: #D97706; }
.rating-low { background-color: #FEF2F2; color: #DC2626; }

.dashboard-wrapper { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.dashboard-body { display: flex; height: 100%; gap: 24px; }

.left-panel {
  flex: 5;
  min-width: 400px;
  flex-shrink: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow-y: auto;
  padding-right: 5px;
}

.right-panel {
  flex: 5;
  min-width: 400px;
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

.video-card {
  height: 100%;
  max-width: 750px;
  margin: 0 auto;
  width: 100%;
}
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-shrink: 0; }
.card-header h3 { margin: 0; font-size: 17px; font-weight: 700; color: #1E293B; }
.status-badge { font-size: 12px; color: teal; background: #F0FDFA; padding: 4px 10px; border-radius: 20px; font-weight: 600; }

.video-area {
  flex: 1; background-color: #F8FAFC; border: 2px dashed #CBD5E1; border-radius: 16px;
  overflow: hidden; position: relative; display: flex; align-items: center; justify-content: center;
  transition: all 0.3s ease; min-height: 240px; margin-bottom: 24px; cursor: pointer;
}
.video-area:hover { border-color: teal; background-color: #F0FDFA; }
.video-area.has-videos { background: white; border: none; padding: 16px; }

.batch-upload-container {
  width: 100%; height: 100%; display: flex; flex-direction: column;
  align-items: center; justify-content: center; padding: 20px; gap: 20px;
}
.batch-upload-container h4 { margin: 0; color: #334155; }
.file-list {
  width: 100%; max-height: 200px; overflow-y: auto; list-style: none;
  padding: 0; margin: 0; gap: 10px; display: flex; flex-direction: column;
}
.file-list li {
  display: flex; justify-content: space-between; align-items: center; padding: 10px;
  background: #F8FAFC; border-radius: 8px; border: 1px solid #E2E8F0; font-size: 14px;
}
.remove-file-btn {
  background: none; border: none; color: #EF4444; font-size: 18px; font-weight: bold;
  cursor: pointer; padding: 0; width: 24px; height: 24px; display: flex; align-items: center;
  justify-content: center; border-radius: 4px; transition: all 0.2s;
}
.remove-file-btn:hover { background: #FEF2F2; transform: scale(1.1); }

.video-with-controls { width: 100%; height: 100%; display: flex; flex-direction: column; gap: 16px; }
.real-video { width: 100%; height: 100%; object-fit: contain; }

.reselect-btn {
  background: teal; color: white; border: none; border-radius: 8px; padding: 10px 20px;
  font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.3s ease;
  align-self: center; box-shadow: 0 4px 12px rgba(0, 128, 128, 0.2);
}
.reselect-btn:hover { background: #006666; transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0, 128, 128, 0.3); }

.upload-placeholder { text-align: center; cursor: pointer; width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.placeholder-img-icon { width: 128px; height: 128px; object-fit: contain; margin-bottom: 20px; opacity: 1; transition: transform 0.3s ease; }
.upload-placeholder:hover .placeholder-img-icon { transform: scale(1.05); }
.upload-title { font-size: 15px; font-weight: 700; color: #334155; margin-bottom: 6px; }
.upload-desc { font-size: 12px; color: #94A3B8; }

.form-area { display: flex; flex-direction: column; gap: 20px; }
.input-group { display: flex; flex-direction: column; gap: 8px; }
.input-group label { font-size: 13px; font-weight: 600; color: #475569; }
.required { color: #EF4444; }
.error-text { font-size: 12px; color: #EF4444; }
.modern-input {
  width: 100%; height: 44px; padding: 0 14px; border: 1px solid #E2E8F0; background: #F8FAFC;
  border-radius: 10px; font-size: 14px; color: #334155; transition: all 0.2s;
}
.modern-input:focus { border-color: teal; background: white; outline: none; box-shadow: 0 0 0 4px rgba(0, 128, 128, 0.1); }
.modern-textarea {
  width: 100%; padding: 10px 14px; border: 1px solid #E2E8F0; background: #F8FAFC;
  border-radius: 10px; font-size: 14px; color: #334155; transition: all 0.2s;
  resize: vertical; min-height: 80px;
}
.modern-select {
  width: 100%; height: 44px; padding: 0 14px; border: 1px solid #E2E8F0; background: #F8FAFC;
  border-radius: 10px; font-size: 14px; color: #334155; transition: all 0.2s;
}

.action-buttons { display: flex; flex-direction: column; gap: 20px; margin-top: 8px; }
.btn-primary {
  height: 44px; background: teal; color: white; border: none; border-radius: 10px;
  font-size: 14px; font-weight: 600; letter-spacing: 0.5px; cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 4px 12px rgba(0, 128, 128, 0.2);
  padding: 0 16px;
}
.btn-primary:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0, 128, 128, 0.3); background: #006666; }
.btn-primary:disabled { background: #CBD5E1; cursor: not-allowed; box-shadow: none; }
.btn-text { background: none; border: none; color: #94A3B8; cursor: pointer; font-size: 13px; font-weight: 500; transition: color 0.2s; }
.btn-text:hover { color: #475569; text-decoration: underline; }
.btn-text.delete-btn { color: #EF4444; }
.btn-secondary {
  background: #1890FF;
  border: 1px solid #1890FF;
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.2);
}
.btn-secondary:hover:not(:disabled) {
  background: #40A9FF;
  border-color: #40A9FF;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(24, 144, 255, 0.3);
}
.btn-secondary:disabled {
  background: #CBD5E1;
  border-color: #CBD5E1;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

.timeline-card { height: 100%; padding: 0; display: flex; flex-direction: column; }
.timeline-header { padding: 24px 28px; border-bottom: 1px solid #F1F5F9; margin: 0; display: flex; justify-content: space-between; align-items: center; flex-shrink: 0; }
.section-title { margin: 0; font-size: 16px; font-weight: 700; color: #1E293B; border-left: 4px solid teal; padding-left: 12px; }
.step-count { font-size: 13px; color: #94A3B8; font-weight: 600; background: #F8FAFC; padding: 4px 10px; border-radius: 12px; }

.step-timeline { flex: 1; overflow-y: auto; padding: 24px 28px; }
.timeline-item { display: flex; gap: 16px; margin-bottom: 24px; position: relative; }
.timeline-marker { width: 12px; height: 12px; border-radius: 50%; background: #E2E8F0; flex-shrink: 0; margin-top: 4px; position: relative; z-index: 1; }
.timeline-item.success .timeline-marker { background: #10B981; }
.timeline-item.error .timeline-marker { background: #EF4444; }
.timeline-item.warning .timeline-marker { background: #F59E0B; }

.timeline-content { flex: 1; background: #f8f9fa; border-radius: 12px; padding: 16px; }
.step-head { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; flex-wrap: wrap; }
.step-head strong { font-size: 15px; font-weight: 700; color: #1E293B; flex: 1; }
.tag { font-size: 12px; padding: 2px 8px; border-radius: 10px; font-weight: 600; }
.tag.success { background: #ECFDF5; color: #059669; }
.tag.error { background: #FEF2F2; color: #DC2626; }
.tag.warning { background: #FFFBEB; color: #D97706; }
.timeline-content p { font-size: 14px; line-height: 1.5; color: #475569; margin: 0; }

.result-left-stack { display: flex; flex-direction: column; gap: 24px; }
.result-right-stack { display: flex; flex-direction: column; gap: 15px; height: 100%; overflow-y: auto; }

.summary-card { padding: 20px; min-height: auto; margin-bottom: 15px; }
.summary-card h4 { margin: 0 0 12px 0; font-size: 16px; font-weight: 700; }
.summary-text { font-size: 14px; line-height: 1.6; color: #333; margin: 10px 0 0 0; padding: 10px; background-color: #f9f9f9; border-radius: 6px; border-left: 3px solid #1890ff; }

.score-points-card { max-height: 600px; overflow-y: auto; }
.step-score-points { margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid #e0e0e0; }
.step-score-points:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
.step-score-points h5 { margin: 0 0 10px 0; font-size: 14px; font-weight: 600; color: #333; }

.score-points-list { margin-left: 20px; }
.score-point-item { display: flex; flex-direction: column; margin-bottom: 10px; padding: 10px; border-radius: 4px; background-color: #f9f9f9; }
.score-point-item.success { border-left: 4px solid #4caf50; background-color: #f1f8e9; }
.score-point-item.fail { border-left: 4px solid #f44336; background-color: #ffebee; }
.score-point-item.warning { border-left: 4px solid #ff9800; background-color: #fff3e0; }

.score-point-header { display: flex; align-items: center; margin-bottom: 5px; }
.status-icon { font-size: 16px; font-weight: bold; margin-right: 10px; min-width: 20px; }
.score-point-item.success .status-icon::before { content: '✓'; background-color: #4caf50; color: white; display: inline-block; width: 16px; height: 16px; border-radius: 50%; text-align: center; line-height: 16px; font-size: 12px; }
.score-point-item.fail .status-icon::before { content: '✗'; background-color: #f44336; color: white; display: inline-block; width: 16px; height: 16px; border-radius: 50%; text-align: center; line-height: 16px; font-size: 12px; }

.point-info { flex: 1; display: flex; flex-direction: column; }
.point-name { font-size: 14px; font-weight: 600; color: #333; margin-bottom: 4px; }
.point-description { font-size: 13px; color: #666; line-height: 1.4; }
.point-score { font-size: 12px; color: #666; font-weight: 500; margin-right: 8px; }
.deduction { margin-left: 8px; font-size: 12px; color: #f44336; font-weight: 500; }
.error-explanation { margin-top: 5px; padding: 8px; background-color: #fff3f3; border-left: 3px solid #f44336; font-size: 12px; color: #d32f2f; border-radius: 4px; margin-left: 25px; }
.no-points { font-size: 13px; color: #999; font-style: italic; margin: 0; }

.function-page { flex: 1; overflow-y: auto; padding-right: 5px; }
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 20px; font-weight: 700; color: #1E293B; margin: 0; }

.classes-page { width: 100%; }
.classes-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; gap: 20px; flex-wrap: wrap; }
.classes-actions { display: flex; gap: 10px; }
.search-container { flex: 1; max-width: 300px; }
.search-input {
  width: 100%; height: 40px; padding: 0 14px; border: 1px solid #E2E8F0; background: #F8FAFC;
  border-radius: 10px; font-size: 14px; color: #334155; transition: all 0.2s;
}
.classes-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.classes-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: #1890ff;
  margin: 0;
}
.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}
.search-box {
  position: relative;
  width: 200px;
}
.search-input {
  width: 100%;
  height: 36px;
  padding: 0 12px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.2s;
}
.search-input:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}
.classes-content { width: 100%; }
.classes-list { display: flex; flex-direction: column; gap: 24px; }
.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}
.course-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;
}
.course-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
.course-image {
  height: 160px;
  overflow: hidden;
}
.course-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.course-info {
  padding: 16px;
}
.course-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}
.course-code {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #666;
}
.course-description {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #666;
  line-height: 1.4;
}
.course-actions {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}
.course-actions .btn-text {
  font-size: 12px;
  padding: 4px 12px;
}
.class-item { background: #fff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); transition: box-shadow 0.3s ease; cursor: pointer; }
.class-item:hover { box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); }
.class-info h4 { margin: 0 0 8px 0; font-size: 16px; font-weight: 600; color: #333; }
.class-info p { margin: 0 0 4px 0; font-size: 14px; color: #666; }
.class-actions { margin-top: 15px; display: flex; gap: 10px; }

.class-detail-header { display: flex; align-items: center; gap: 20px; margin-bottom: 24px; flex-wrap: wrap; }
.class-detail-header h3 { margin: 0; font-size: 18px; font-weight: 600; color: #333; flex: 1; }
.class-detail-actions { display: flex; gap: 10px; }
.class-detail-content { width: 100%; }
.student-list { display: flex; flex-direction: column; gap: 12px; }
.student-item { display: flex; justify-content: space-between; align-items: center; padding: 16px; background: #f8f9fa; border-radius: 10px; }
.student-info p { margin: 0 0 4px 0; font-size: 14px; color: #666; }
.student-actions { display: flex; gap: 10px; }

.exams-page { width: 100%; }
.exams-header { margin-bottom: 20px; }
.tab-buttons { display: flex; margin-bottom: 20px; border-bottom: 1px solid #e0e0e0; }
.tab-btn { padding: 10px 20px; border: none; background: none; cursor: pointer; font-size: 14px; color: #666; border-bottom: 2px solid transparent; transition: all 0.3s ease; }
.tab-btn.active { color: #1890ff; border-bottom-color: #1890ff; }
.exams-content { width: 100%; }
.exams-actions { margin-bottom: 20px; }
.exams-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
.exam-item { background: #fff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); transition: box-shadow 0.3s ease; }
.exam-item:hover { box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15); }
.exam-info h4 { margin: 0 0 10px 0; font-size: 16px; font-weight: 600; color: #333; }
.exam-info p { margin: 0 0 8px 0; font-size: 14px; color: #666; line-height: 1.4; }
.exam-actions { margin-top: 15px; display: flex; gap: 10px; }

.templates-content { width: 100%; }
.templates-actions { margin-bottom: 20px; }
.templates-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
.template-item { background: #fff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); transition: box-shadow 0.3s ease; }
.template-item:hover { box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15); }
.template-info h4 { margin: 0 0 10px 0; font-size: 16px; font-weight: 600; color: #333; }
.template-info p { margin: 0 0 8px 0; font-size: 14px; color: #666; line-height: 1.4; }
.template-actions { margin-top: 15px; display: flex; gap: 10px; }

.messages-page { width: 100%; overflow: hidden; }
.messages-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid #E2E8F0; }
.mark-all-read-btn { color: #1890ff; font-weight: 600; font-size: 14px; }
.messages-content { width: 100%; }
.notifications-list { display: flex; flex-direction: column; gap: 12px; max-height: 600px; overflow-y: auto; padding-right: 8px; }
.notification-item { display: flex; padding: 16px 20px; background: #ffffff; border-radius: 12px; border: 1px solid #E2E8F0; cursor: pointer; transition: all 0.2s ease; position: relative; }
.notification-item:hover { box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); transform: translateY(-2px); }
.notification-item.unread { background: #f0f9ff; border-left: 4px solid #1890ff; }
.unread-indicator { width: 4px; background: #1890ff; border-radius: 2px; margin-right: 16px; flex-shrink: 0; }
.notification-content { flex: 1; min-width: 0; }
.notification-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.notification-header h4 { margin: 0; font-size: 16px; font-weight: 500; color: #64748b; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: calc(100% - 60px); }
.notification-header .unread-title { font-weight: 700; color: #1e293b; }
.unread-tag { display: inline-block; padding: 2px 8px; background: #ff4d4f; color: white; border-radius: 10px; font-size: 12px; font-weight: 600; flex-shrink: 0; }
.notification-body { margin: 0 0 12px 0; font-size: 14px; color: #475569; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.notification-footer { display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #94a3b8; }
.sender-name { font-weight: 500; }
.empty-notifications, .loading-state { text-align: center; padding: 60px 20px; color: #94a3b8; background: #f9fafb; border-radius: 12px; border: 1px dashed #E2E8F0; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 16px; margin-top: 20px; padding-top: 16px; border-top: 1px solid #E2E8F0; }
.pagination button { padding: 6px 16px; background: white; border: 1px solid #E2E8F0; border-radius: 6px; cursor: pointer; transition: all 0.2s; font-size: 14px; color: #334155; }
.pagination button:hover:not(:disabled) { background: #f0f9ff; border-color: #1890ff; color: #1890ff; }
.pagination button:disabled { opacity: 0.5; cursor: not-allowed; }
.pagination span { font-size: 14px; color: #64748b; font-weight: 500; }

.page-content { min-height: 600px; }
.profile-tabs { display: flex; gap: 10px; margin-bottom: 30px; border-bottom: 1px solid #E2E8F0; }
.profile-tabs .tab-btn { padding: 10px 20px; border: none; background: none; cursor: pointer; font-size: 14px; color: #666; border-bottom: 2px solid transparent; transition: all 0.3s ease; }
.profile-tabs .tab-btn.active { color: #1890ff; border-bottom-color: #1890ff; }
.profile-content { padding: 20px 0; }
.profile-item { margin-bottom: 20px; }
.profile-row { display: flex; align-items: center; gap: 12px; }
.profile-label { font-size: 18px; color: #666; min-width: 80px; }
.profile-value { font-size: 18px; color: #333; }
.radio-label { margin-right: 20px; cursor: pointer; font-size: 18px; }
.edit-btn, .add-btn { margin-left: 10px; padding: 4px 12px; background: #1890ff; color: white; border: none; border-radius: 4px; font-size: 12px; cursor: pointer; }
.profile-actions { margin-top: 30px; padding-top: 20px; border-top: 1px solid #E2E8F0; text-align: center; }
.logout-btn { padding: 10px 24px; background: #ff4d4f; color: white; border: none; border-radius: 8px; font-size: 14px; cursor: pointer; }

.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(0, 0, 0, 0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: white; border-radius: 16px; padding: 30px; width: 90%; max-width: 500px; position: relative; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1); }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.modal-header h3 { margin: 0; font-size: 18px; font-weight: 600; color: #333; }
.modal-body {
  padding: 0 20px;
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 30px;
  padding: 0 20px 20px;
}
.template-modal {
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}
.template-detail-page {
  padding: 20px 0;
}
.detail-header {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  gap: 20px;
}
.detail-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #333;
}
.template-detail-content {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  line-height: 1.6;
  color: #333;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.template-meta {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e0e0e0;
}
.template-meta p {
  margin: 8px 0;
}
.template-steps {
  margin-top: 24px;
}
.template-steps h4 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #24292e;
  padding-bottom: 8px;
  border-bottom: 2px solid #e1e4e8;
}
.template-step h5 {
  font-size: 16px;
  font-weight: 600;
  margin: 20px 0 15px 0;
  color: #24292e;
  padding-left: 10px;
  border-left: 4px solid #0366d6;
}
.template-step h4 {
  font-size: 16px;
  font-weight: 600;
  margin: 15px 0 10px 0;
  color: #24292e;
  padding-left: 0;
}
.score-point {
  margin-bottom: 20px;
  padding-left: 30px;
  border-left: 3px solid #e1e4e8;
}
.score-point-details {
  padding-left: 30px;
}
.score-point p {
  margin: 8px 0;
  line-height: 1.5;
  font-size: 14px;
}
.score-point strong {
  color: #24292e;
  font-weight: 600;
}
.step-container { border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; margin-bottom: 20px; background: #f9f9f9; }
.step-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.step-header h4 { margin: 0; font-size: 16px; font-weight: 600; color: #333; }
.score-points-container { margin-top: 20px; border-top: 1px solid #e0e0e0; padding-top: 20px; }
.score-points-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.score-points-header h5 { margin: 0; font-size: 14px; font-weight: 600; color: #333; }
.form-row { display: flex; gap: 15px; margin-bottom: 15px; }
.form-group {
  margin-bottom: 20px;
}
.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #475569;
}
.form-group.half { flex: 2; }
.form-group.quarter { flex: 1; }
.add-step-btn { margin-top: 10px; display: inline-block; }

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; border-radius: 3px; }
::-webkit-scrollbar-thumb { background-color: rgba(148, 163, 184, 0.3); border-radius: 4px; transition: background-color 0.2s; }
::-webkit-scrollbar-thumb:hover { background-color: rgba(148, 163, 184, 0.6); }
* { scrollbar-width: thin; scrollbar-color: rgba(148, 163, 184, 0.3) transparent; }

.nav-item { position: relative; }
.unread-badge { position: absolute; top: 4px; right: 8px; min-width: 18px; height: 18px; padding: 0 5px; background: #ff4d4f; color: white; border-radius: 9px; font-size: 11px; font-weight: 700; display: flex; align-items: center; justify-content: center; animation: badge-bounce 0.3s ease-out; z-index: 10; }
@keyframes badge-bounce { 0% { transform: scale(0); } 50% { transform: scale(1.2); } 100% { transform: scale(1); } }

.step-score { font-size: 12px; color: #666; font-weight: 500; margin-left: 10px; }
</style>
