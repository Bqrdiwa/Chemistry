
function toggleLoading(){
    var loadingCont = document.getElementById('loading-base')
    if(loadingCont.style.display == 'flex'){
        loadingCont.style.display = 'none'
    }else{
        loadingCont.style.display = 'flex'
    }
}


function openSocial(mode=true){
    let socialCont = document.getElementById('socialCont')
    if(mode){
        socialCont.style.display ='flex'
    }else{
        socialCont.style.display ='none'
    }


    
}