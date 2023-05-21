
//event listener that triggers when key up > axios request to server> look in the api_data table if user input is include in the db
// then return the values

$('#ingredient_name').keyup(async (e)=> {
    let userInput = $('#ingredient_name').val().trim();
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
    $('#ingredient_name').val(selectedValue);
    $('#suggestions').empty();
    $('#suggestions-container').removeClass('border-visible');
  });

const displayRecipe = (data) => {
    for (let recipe of data){
        let $recipeDiv = $('<div>');
        let $img = $('<img>').attr('src', recipe.image).attr('alt', `${recipe.title} recipe`);
        let $h1 = $('<h1>').text(recipe.title);
        let $h3 = $('<h3>').text('Ingredients');
        let $ul = $('<ul>');
        for (let ingredient of recipe.ingredients){
            let $li = $('<li>');
            $li.text(ingredient);
            $ul.append($li);
        }
        $recipeDiv.append($img,$h1, $h3, $ul);
        $('body').append($recipeDiv);
    }
}

$('.api-call-button').on('click', async (e) => {
    let itemName = $(e.target).attr('id');
    
    let res = await axios.post('/fetch-recipes', {'ingredientName':itemName})
    let data = res.data;
    
    displayRecipe(data);
})
