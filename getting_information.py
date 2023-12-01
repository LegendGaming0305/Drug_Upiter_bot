async def get_categories() -> dict:
    from new_handlers import USER_SEARCH_DATA
    categories = {}
    producer = USER_SEARCH_DATA['Producer'].tolist()
    for i, prod in enumerate(producer):
        if prod not in categories.values():
            categories[i] = prod

    return categories

async def get_subcategories(category) -> dict:
    from new_handlers import USER_SEARCH_DATA
    from inline_menu_for_analogs import GLOBAL_LIST_OF_MENU
    subcategories = {}
    dosage_from = USER_SEARCH_DATA.loc[USER_SEARCH_DATA['Producer'] == GLOBAL_LIST_OF_MENU[category]]['Dosage_form'].tolist()
    for i, form in enumerate(dosage_from):
        if form not in subcategories.values():
            subcategories[i] = form

    return subcategories

async def get_sub_subcategories(category, subcategory) -> dict:
    from new_handlers import USER_SEARCH_DATA
    from inline_menu_for_analogs import GLOBAL_LIST_OF_MENU
    sub_subcategories = {}
    dose = USER_SEARCH_DATA.loc[(USER_SEARCH_DATA['Producer'] == GLOBAL_LIST_OF_MENU[category]) & 
                                (USER_SEARCH_DATA['Dosage_form'] == GLOBAL_LIST_OF_MENU[subcategory])]['Dose'].tolist()
    for i, dose_number in enumerate(dose):
        if dose_number not in sub_subcategories.values():
            sub_subcategories[i] = dose_number
    
    return sub_subcategories