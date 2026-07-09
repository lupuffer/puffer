<template>
  <body class="page-body">
    <div class="nav-wrapper-div">
      <div class="nav-inner-container">
        <div class="nav-brand-span">{{ info.name.zh }} ({{ info.name.en }})</div>
        <div class="nav-links-box">
          <a href="#about" class="nav-anchor-link">关于我</a>
          <a href="#research" class="nav-anchor-link">研究方向</a>
          <a href="#projects" class="nav-anchor-link">项目经验</a>
          <a href="#awards" class="nav-anchor-link">获奖情况</a>
          <a href="#books" class="nav-anchor-link">最近阅读</a>
        </div>
      </div>
    </div>

    <div class="main-wrapper-div">
      <div class="section-container" id="about">
        <div class="section-title-h2">关于我</div>
        <div class="profile-flex-row">
          <div class="profile-left-side">
            <div class="avatar-frame-div">
              <img :src="info.avatar" :alt="info.name.zh" class="avatar-img-obj">
            </div>
            <div class="name-info-div">
              <div class="name-zh-div">{{ info.name.zh }}</div>
              <div class="name-en-div">{{ info.name.en }}</div>
              <p class="info-status-p">
                <span class="status-span">{{ info.status }} · </span>
                <a :href="info.school.url" target="_blank" class="link-blue-a">{{ info.school.name }}</a>
              </p>
            </div>
            <div class="contact-card-box">
              <p class="contact-line-p"><span class="label-bold-span">邮箱：</span>{{ info.contact.email }}</p>
              <p class="contact-line-p"><span class="label-bold-span">电话：</span>{{ info.contact.phone }}</p>
              <p class="contact-line-p"><span class="label-bold-span">地址：</span>{{ info.contact.address }}</p>
              <p v-if="info.repository" class="contact-line-p repo-line">
                <span class="label-bold-span">🔗 代码仓库：</span>
                <a :href="info.repository.url" target="_blank" class="link-blue-a">{{ info.repository.url }}</a>
              </p>
            </div>
          </div>

          <div class="detail-right-side">
            <div class="card-grey-div">
              <div class="card-sub-h3">专业背景</div>
              <div class="grid-2col-layout">
                <div class="grid-cell-div"><span class="label-bold-span">专业：</span>{{ info.major }}</div>
                <div class="grid-cell-div"><span class="label-bold-span">籍贯：</span>{{ info.hometown }}</div>
                <div class="grid-cell-div"><span class="label-bold-span">入学：</span>{{ info.enrollment }}</div>
                <div class="grid-cell-div"><span class="label-bold-span">毕业：</span>{{ info.graduation }}</div>
              </div>
            </div>

            <div class="card-grey-div">
              <div class="card-sub-h3">教育经历</div>
              <div v-for="(edu, index) in info.education" :key="index" class="edu-item-box">
                <div class="edu-top-flex">
                  <span class="edu-title-span">{{ edu.school }}</span>
                  <span class="edu-date-span">{{ edu.date }}</span>
                </div>
                <p class="edu-p-main">{{ edu.major }}</p>
                <p class="edu-p-small">{{ edu.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="section-container" id="research">
        <div class="section-title-h2">研究方向</div>
        <div class="quote-box-div">
          <p class="quote-p-text">"{{ info.research.quote }}"</p>
        </div>
        <div class="feature-grid-row">
          <div v-for="(area, index) in info.research.areas" :key="index" class="feature-card-div">
            <div class="feature-head-div">{{ area.icon }} {{ area.title }}</div>
            <p class="feature-p-desc">{{ area.description }}</p>
          </div>
        </div>

        <div v-if="info.research.politicalEconomy" class="card-grey-div" style="margin-top: 30px;">
          <div class="card-sub-h3">{{ info.research.politicalEconomy.title }}</div>
          <p style="margin-bottom: 20px;">{{ info.research.politicalEconomy.description }}</p>
          <div class="feature-grid-row">
            <div v-for="(theory, index) in info.research.politicalEconomy.theories" :key="index" class="feature-card-div">
              <div class="feature-head-div">{{ theory.name }}</div>
              <p class="feature-p-desc">{{ theory.description }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== 项目经验 ===== -->
      <div class="section-container" id="projects">
        <div class="section-title-h2">项目经验 (Projects)</div>
        <p class="section-subtitle-p">以下项目源码与详细文档均托管于 <a :href="info.repository.url" target="_blank" class="link-blue-a">{{ info.repository.url }}</a></p>

        <div v-for="project in info.projects" :key="project.id" class="project-card-div">
          <div class="project-header-flex">
            <div class="project-title-left">
              <span class="project-icon-span">{{ project.icon }}</span>
              <div>
                <div class="project-name-div">{{ project.name }}</div>
                <div class="project-name-en-div">{{ project.nameEn }}</div>
              </div>
            </div>
            <div class="project-meta-right">
              <span class="project-date-span">{{ project.date }}</span>
              <span class="project-role-span">{{ project.role }}</span>
            </div>
          </div>

          <p class="project-summary-p">{{ project.summary }}</p>

          <div class="project-tech-row">
            <span v-for="tech in project.techStack" :key="tech" class="tech-tag-span">{{ tech }}</span>
          </div>

          <div class="project-highlights-box">
            <div class="project-highlights-title">核心亮点</div>
            <ul class="project-ul">
              <li v-for="(highlight, hIdx) in project.highlights" :key="hIdx" class="project-li">{{ highlight }}</li>
            </ul>
          </div>

          <div class="project-links-row">
            <a :href="project.repoUrl" target="_blank" class="project-link-a">📂 项目源码</a>
            <a :href="project.docUrl" target="_blank" class="project-link-a">📄 详细文档</a>
          </div>
        </div>
      </div>

      <div class="section-container" id="awards">
        <div class="section-title-h2">获奖情况</div>
        <div class="award-list-box">
          <div v-for="(award, index) in info.awards" :key="index" class="award-item-div">
            <i class="award-dot-i">●</i> {{ award.title }}
            <span v-if="award.tag" class="tag-bold-span">{{ award.tag }}</span>
          </div>
        </div>
      </div>

      <div class="section-container" id="books">
        <div class="section-title-h2">最近阅读 (Selected Readings)</div>
        <div class="book-stack-div">
          <div v-for="book in books" :key="book.id" class="book-row-div">
            <div class="book-img-side-div"><img :src="book.image" :alt="book.title" class="book-img-obj"></div>
            <div class="book-body-div">
              <div class="book-title-div">{{ book.title }}</div>
              <p class="book-meta-p">作者：{{ book.author }} | {{ book.date }}</p>
              <div v-if="book.badge" class="book-badge-div">{{ book.badge }}</div>
              <div class="book-desc-div">{{ book.description }}</div>
              <a :href="book.buyUrl" class="buy-btn-a">京东购买</a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="footer-div">
      <div class="footer-inner-div">
        <a href="#" class="top-link-a">返回顶部 ↑</a>
        <p class="footer-p">© 2026 {{ info.name.zh }} | {{ info.school.name }} | <a :href="info.repository.url" target="_blank" class="footer-repo-a">个人仓库</a></p>
      </div>
    </div>
  </body>
</template>

<script setup>
import { onMounted } from 'vue'
import { useData } from './assets/data.js'

const { info, books, loadData } = useData()

onMounted(() => {
  loadData()
})
</script>

<style>
/* 样式已迁移到 src/assets/main.css */
</style>