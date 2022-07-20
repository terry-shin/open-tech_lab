<template>
  <div>
    <input type="email" name="email" required="required" placeholder="E-mail" v-model="user.email" class="border-2 h-12 w-10/12 mb-5">
    <br>
    <input type="password" name="passWord" required="required" placeholder="PassWord" v-model="user.password" class="border-2 h-12 w-10/12 mb-5">
    <br>
    <v-btn @click="SignIn" class="h-12 w-10/12 my-4 bg-green-300">ログイン</v-btn>
  </div>
</template>

<script>
import { getAuth, signInWithEmailAndPassword } from 'firebase/auth'
export default {
  name: "LogIn",
  data () {
    return {
      user:{
        email: '',
        password: '',
      }
    }
  },
  methods: {
    SignIn () {
      try {
        const auth = getAuth();

        signInWithEmailAndPassword(auth, this.user.email, this.user.password)
          .then((user) => {
            alert("ログインしました");
            this.$router.push("/login_success");
          })
          .catch((error) => {
            console.error(error)
          })
      } catch (e) {
        console.error(e)
      }
    }
  }
}
</script>