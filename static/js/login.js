function userLogin() {
    return {
      user: {
        email:'manav@gmail.com',
        password:'manav'
      },
      errorText: '',
      isLoading:false,

      async submitForm(return_page,home_url, go_url) {
        debugger;
        this.isLoading = true;
        debugger;
        await fetch(go_url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json;charset=utf-8'
          },
          body: JSON.stringify(this.user)
        })
        .then((response) => {
          debugger;
          if (response.status == 200) {
            return response.json();
          }
          return Promise.reject(response);
        })
        .then((data) => {
          debugger
          this.isLoading =false;
          window.location.replace(home_url+return_page);
          
        })
        .catch((err) => {
          this.isLoading =false;
          err.json().then(errdata =>{
            debugger;
            alert(errdata.detail)
          })
          debugger;
        })
        .finally(()=>{
          console.log("succcess")
        });
      }
    };
  }
  