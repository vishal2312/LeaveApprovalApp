function userResetPassword() {
    return {
      user: {
        new_password: '',
        confirm_password: ''
      },
      errorText: '',
      isModalOpen: false,
      isLoading:false,

      async submitForm(token) {
        this.isLoading = true;
        debugger;
        await fetch(API_URL + API_RESET_PASSWORD_URL + '?token=' + token, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json;charset=utf-8'
          },
          body: JSON.stringify(this.user)
        })
        .then((response) => {
          debugger;
          if (response.ok) {
            return response.json();
          }
          return Promise.reject(response);
        })
        .then((data) => {
          this.isLoading =false;
          this.isModalOpen = true;
          // window.location.replace(APP_URL + API_LOGIN_URL);
          
        })
        .catch((err) => {
          this.isLoading =false;
          err.json().then(errdata =>{
            alert(errdata.detail);
          });
          debugger;
        });
      },
  
      closeModal() {
        this.isModalOpen = false;
        window.location.replace(APP_URL + API_LOGIN_URL);
      }
    };
  }
  