import{r as s}from"./index.63692a27.js";import"./element-plus.82ea873e.js";function u(e,t="or"){const o=typeof e=="string"?[e]:e,n=s.currentRoute.value.meta.permission||[];return t==="and"?o.every(r=>n.includes(r)):o.some(r=>n.includes(r))}const c=(e,t)=>{const o=typeof t.value=="string"?[t.value]:t.value,a=t.arg==="and"?"and":"or";u(o,a)||e.parentNode&&e.parentNode.removeChild(e)};var d=e=>{e.directive("action",{mounted:(t,o)=>c(t,o)})};export{d as default};
