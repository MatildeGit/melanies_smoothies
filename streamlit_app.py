s# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
#my_dataframe = session.table("smoothies.public.orders").filter(col("ORDER_FILLED")==0).collect()
#st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    ,my_dataframe
    ,max_selections=5 #to limit the fruits added to an order
)

if ingredients_list:
    ingredients_string=''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '#add this to what is already in the variable
        st.subheader(fruit_chosen + 'Nutrition Information')
        # new section to display smoothiefroot nutrition information
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/"+fruit_chosen)
        #st.text(smoothiefroot_response.json())
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True) 

    #st.write(ingredients_string)

my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""
#st.write(my_insert_stmt)
#st.stop()

#st.write(my_insert_stmt)
time_to_insert = st.button('Submit Order')

if time_to_insert:
    session.sql(my_insert_stmt).collect() # add to the database 
    st.success('Your Smoothie is ordered!', icon="✅")
    
session = get_active_session()
my_dataframe = session.table("smoothies.public.orders").filter(col("ORDER_FILLED")==0).collect()

if my_dataframe:
    editable_df = st.data_editor(my_dataframe)
    submitted = st.button('Submit')
    if submitted:
         og_dataset = session.table("smoothies.public.orders")
         edited_dataset = session.create_dataframe(editable_df)

         try:
            og_dataset.merge(edited_dataset
                , (og_dataset['ORDER_UID'] == edited_dataset['ORDER_UID'])
                , [when_matched().update({'ORDER_FILLED': edited_dataset['ORDER_FILLED']})]
                ); 
            st.success('Someone clicked the button', icon = '👍')
         except:
            st.write('Something went wrong.')
else:
    st.success('There are no pending orders right now', icon='👍')




