
//event listener that triggers when key up > axios request to server> look in the api_data table if user input is include in the db
// then return the values

$('#ingredient').keyup(async (e)=> {
    let userInput = $('#ingredient').val().trim();
    if (userInput === '') {
        $('#suggestions').empty();
        $('#suggestions-container').removeClass('border-visible');
    } else {
        let res = await axios.get('/search', { params: { userInput } });
        let data = res.data;
        if (data.response.length > 0) {
            $('#suggestions').empty();
            
            for(let i=0; i < data.response.length; i++ ){
                let newLi = $('<li>')
                newLi.text(data.response[i].name)
                $('#suggestions').append(newLi)
            }
            $('#suggestions-container').addClass('border-visible');
        } else {
            $('#suggestions').empty();
            $('#suggestions-container').removeClass('border-visible');
            $('#suggestions').css('height', '0');
        }
    }
});

const showSuggestions = (results)=> {
    for(let result of results.response){
        let newLi = $('<li>')
        newLi.text(result)
        $('#suggestions').append(newLi)
    }
}

$('#suggestions').on('click', 'li', function() {
    let selectedValue = $(this).text();
    $('#ingredient').val(selectedValue);
    $('#suggestions').empty();
    $('#suggestions-container').removeClass('border-visible');
  });