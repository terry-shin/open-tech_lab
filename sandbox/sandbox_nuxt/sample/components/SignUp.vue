<template>
  <div>
    <input type="email" name="email" required="required" placeholder="E-mail" v-model="user.email" class="border-2 h-12 w-10/12 mb-5">
    <br>
    <input type="password" name="passWord" required="required" placeholder="PassWord" v-model="user.password" class="border-2 h-12 w-10/12 mb-5">
    <br>
    <v-btn @click="register" class="h-12 w-10/12 my-4 bg-green-300">登録</v-btn>
  </div>
</template>

<script>
import { getAuth, onAuthStateChanged, createUserWithEmailAndPassword } from 'firebase/auth'
export default {
  name: "SignUp",
  data () {
    return {
      user:{
          email: '',
          password: '',
        }
    }
 },
 methods: {
   register () {
      const auth = getAuth()
      createUserWithEmailAndPassword(auth,this.user.email,this.user.password)
        .then(function(user){
                alert("登録しました");
             })
            .catch((error) => {
              alert(error.message)
              console.error(error)
            })
      //.thenは成功する時に使用される、つまりメールアドレスとパスワードの登録が成功した時の処理。（失敗したときは.catch）
      //本来はここから別ページに飛ぶ等の処理を追加していく。
   },
 },
}
</script>