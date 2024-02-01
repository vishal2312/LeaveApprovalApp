function adminLogin(){
    return{
        user:{
            email:'',
            password:''
        },
        errorText:'',
        submitForm(return_page,home_url, go_url){
            debugger;
            fetch(go_url,{
                method:'POST',
                headers: {
                    'Content-Type': 
                        'application/json;charset=utf-8'
                  },
                body: JSON.stringify(this.user)
            })
            .then((response)=>{
                debugger;
                if (response.status === 200){
                    window.location.replace(home_url+return_page)
                }
                else if (response.status===403){
                    this.errorText = LOGIN_ERROR_TEXT
                    this.isNotValid = true
                }
                else{
                    this.errorText = SOMETHING_WRONG
                    this.isNotValid = true
                } debugger;
            })
            .finally(() => {
                this.buttonLabel = "Log In"
                this.loading = false
            
              })
        },
        async init(){
            
        }
    }
}
