var s=e=>{e.directive("src",{beforeMount(t,r){const{value:a}=r,c="http://127.0.0.1:8000/api".replace("api","media/")+a;t.setAttribute("src",c)}})};export{s as default};
