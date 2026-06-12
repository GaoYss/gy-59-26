<script setup>
import { onMounted, reactive, ref } from 'vue'
import { Plus, RefreshCcw } from 'lucide-vue-next'

import { reviewApi } from '../api/modules'
import DataTable from '../components/DataTable.vue'
import EmptyState from '../components/EmptyState.vue'
import MessageBar from '../components/MessageBar.vue'
import StatusBadge from '../components/StatusBadge.vue'
import { reviewResults, reviewStatuses, subjects } from '../constants/options'

const reviews = ref([])
const loading = ref(false)
const saving = ref(false)
const message = reactive({ text: '', type: 'info' })
const form = reactive({
  studentName: '',
  subject: '科目二',
  originalScore: 0,
  reason: ''
})

const columns = [
  { key: 'studentName', label: '学员' },
  { key: 'subject', label: '科目' },
  { key: 'originalScore', label: '原成绩' },
  { key: 'reason', label: '申请原因' },
  { key: 'status', label: '处理状态' },
  { key: 'result', label: '复核结果' },
  { key: 'reviewedAt', label: '复核时间' }
]

async function loadReviews() {
  loading.value = true
  try {
    reviews.value = await reviewApi.list()
  } catch (error) {
    message.text = error.message
    message.type = 'error'
  } finally {
    loading.value = false
  }
}

async function createReview() {
  saving.value = true
  message.text = ''
  try {
    await reviewApi.create({ ...form })
    Object.assign(form, {
      studentName: '',
      subject: form.subject,
      originalScore: 0,
      reason: ''
    })
    message.text = '复核申请已提交'
    message.type = 'success'
    await loadReviews()
  } catch (error) {
    message.text = error.message
    message.type = 'error'
  } finally {
    saving.value = false
  }
}

async function updateReview(row, payload) {
  try {
    await reviewApi.update(row.id, payload)
    await loadReviews()
  } catch (error) {
    message.text = error.message
    message.type = 'error'
  }
}

onMounted(loadReviews)
</script>

<template>
  <section class="module-grid two-columns">
    <form class="panel form-panel" @submit.prevent="createReview">
      <div class="panel-heading">
        <div>
          <h3>成绩复核申请</h3>
          <p>学员对考试成绩有异议时可提交复核申请。</p>
        </div>
        <Plus :size="20" />
      </div>

      <MessageBar :message="message.text" :type="message.type" />

      <label>
        <span>学员姓名</span>
        <input v-model.trim="form.studentName" required placeholder="请输入姓名" />
      </label>
      <div class="field-row">
        <label>
          <span>科目</span>
          <select v-model="form.subject">
            <option v-for="subject in subjects" :key="subject">{{ subject }}</option>
          </select>
        </label>
        <label>
          <span>原成绩</span>
          <input v-model.number="form.originalScore" min="0" max="100" type="number" />
        </label>
      </div>
      <label>
        <span>申请原因</span>
        <textarea v-model.trim="form.reason" rows="3" required placeholder="请说明复核原因"></textarea>
      </label>

      <button class="primary-button" :disabled="saving" type="submit">
        <Plus :size="18" />
        <span>{{ saving ? '提交中' : '提交申请' }}</span>
      </button>
    </form>

    <section class="panel list-panel">
      <div class="panel-heading">
        <div>
          <h3>复核列表</h3>
          <p>查看复核申请的处理状态与复核结果。</p>
        </div>
        <button class="icon-button" type="button" title="刷新" @click="loadReviews">
          <RefreshCcw :size="18" />
        </button>
      </div>

      <EmptyState v-if="!loading && reviews.length === 0" title="暂无复核申请" description="复核申请将在这里显示。" />
      <DataTable v-else :columns="columns" :rows="reviews">
        <template #status="{ row }">
          <StatusBadge :status="row.status" />
        </template>
        <template #result="{ row }">
          <span v-if="row.result">{{ row.result }}</span>
          <span v-else class="text-muted">-</span>
        </template>
        <template #reviewedAt="{ row }">
          <span v-if="row.reviewedAt">{{ row.reviewedAt }}</span>
          <span v-else class="text-muted">-</span>
        </template>
        <template #actions="{ row }">
          <div class="action-group">
            <select
              v-if="row.status !== '已完成'"
              class="compact-select"
              :value="row.status"
              @change="updateReview(row, { status: $event.target.value })"
            >
              <option v-for="status in reviewStatuses" :key="status">{{ status }}</option>
            </select>
            <select
              v-if="row.status === '审核中'"
              class="compact-select"
              @change="updateReview(row, { result: $event.target.value })"
            >
              <option value="">选择复核结果</option>
              <option v-for="result in reviewResults" :key="result" :value="result">{{ result }}</option>
            </select>
          </div>
        </template>
      </DataTable>
    </section>
  </section>
</template>
