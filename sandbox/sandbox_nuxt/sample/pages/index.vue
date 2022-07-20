<template>
    <div class="relative flex items-top justify-center min-h-screen bg-gray-100 sm:items-center sm:pt-0">
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.1.2/dist/tailwind.min.css" rel="stylesheet">
        <div class="max-w-4xl mx-auto sm:px-6 lg:px-8">
            <div class="mt-8 bg-white overflow-hidden shadow sm:rounded-lg p-6">
                <h2 class="text-2xl leading-7 font-semibold">テストページ：ログイン</h2>
                <LogIn/>
                <hr>
                <a href="./regist">ユーザー登録へ</a>
            </div>
        </div>
    </div>
</template>

<script>
import LogIn from '@/components/LogIn.vue'

export default {
  name: 'index',
  components: {
    LogIn
  }
}

</script>
