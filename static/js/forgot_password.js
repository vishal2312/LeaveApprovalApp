function userForgotPassword() {
    return {
      user: {
        email: ''
      },
      errorText: '',
      isModalOpen: false,
      isLoading:false,

      async submitForm() {
        this.isLoading = true;
        debugger;
        await fetch(API_URL + API_FORGOT_PASSWORD_URL, {
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
          this.isLoading = false;
          this.isModalOpen = true;
          // window.location.replace(APP_URL + API_LOGIN_URL);
          
        })
        .catch((err) => {
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
  