var loadingCont = document.getElementById('loading-base')
function toggleLoading(){
    if(loadingCont.style.display == 'flex'){
        loadingCont.style.display = 'none'
    }else{
        loadingCont.style.display = 'flex'
    }
}
console.log('connected')