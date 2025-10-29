const interval = 60 * 1000;

let loopCycle = 0;

let cookies;
let proxy;


function searchForClothes() {
    loopCycle += 1;
    params = getParams();
    if (params.categories.length > 0) {
        if (cookies && proxy) {
            get_clothes(loopCycle, params);
        } else {
            setup_cookies().then(() => get_clothes(loopCycle, params));
        }
    }
}

function get_clothes(currentCycle, params) {
    if (currentCycle == loopCycle) {
        try {
            fetch("client/get_clothes/", {
                method: "POST",
                body: JSON.stringify({
                    cookies: cookies,
                    proxy: proxy,
                    params: params,
                })
            })
            .then(response => {
                if (response.status == 200) {
                    return response.json()
                } else if (response.status == 403 || response.status == 401) {
                    setup_cookies().then(() => get_clothes(currentCycle, params));   
                }
                throw new Error("[get_clothes] Error accessing Vinted");
            })
            .then(data => {
                populateCards(data.items);

                setTimeout(function() {
                    get_clothes(currentCycle, params);
                }, interval)
            });
        } catch (e) {
            console.error(e);
        }
    }
}

async function setup_cookies() {
    try {
        await fetch("client/setup_session/")
        .then(response => {
            if (response.status == 200) {
                return response.json()
            }
            throw new Error("[setup_cookies] Error accessing Vinted");
        })
        .then(data => {
            cookies = data.cookies;
            proxy = data.proxy;
        });
    } catch (e) {
        console.error(e);
        await setup_cookies();
    }
}

function getParams() {
    const categories = $.map(
        $(".form-check input[name='Catégorie']").filter(":checked"), 
        (checkbox) => $(checkbox).attr("value").split("-")
    );
    const brands = $.map(
        $(".form-check input[name='Marques']").filter(":checked"), 
        (checkbox) => $(checkbox).attr("value").split("-")
    );
    const sizes = $.map(
        $(".form-check input[name='Tailles']").filter(":checked"), 
        (checkbox) => $(checkbox).attr("value")
    );
    const price = $("#price-value").html();
    return {
        categories: categories,
        brands: brands,
        sizes: sizes,
        price: price,
    }
}

function populateCards(data) {
    let cards = "";
    for (const info of data) {
        cards += `
        <div class="col">
            <a href="${info.url}" style="text-decoration:none" target="_blank">
                <div class="card mx-auto mb-5 ${info.seen == "old" ? "bg-white" : "bg-new"}" style="width: 16rem;">
                    <div style="height: 20rem;">
                        <img src="${info.img}" class="card-img-top" title="${info.title}"
                        style="width: 100%; height: 100%; object-fit: cover;">
                    </div>
                    <div class="card-body">
                        <div class="row align-items-center">
                            <div class="col-4">
                                <span class="h5">${info.price}€</span>    
                            </div>
                            <div class="col-8 d-flex flex-column align-items-end">
                                <span><small>${info.status}</small></span>
                                <span><small>${info.size}</small></span>
                                <span><small>${info.brand == "" ? "Sans marque" : info.brand}</small></span>
                                <!--span><small>${info.id}</small></span-->
                            </div>
                        </div>
                    </div>
                </div>
            </a>            
        </div>`
    }
    $("#results").html(cards);
}

$('.section-title').click(function () {
    const children_boxes = $(this).siblings().find("input");
    if (children_boxes.filter(":checked").length == children_boxes.length){
        children_boxes.prop("checked", false);
    } else {
        children_boxes.prop("checked", true);
    }
});

$('#price-range').on('input', function() {
    $('#price-value').html(this.value);
});