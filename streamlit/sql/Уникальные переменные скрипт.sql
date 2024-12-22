select distinct new_id, name_rus from  (select date_loc, value, catalog_id, site_id, new_id,  name_rus from data.data_value as value left join 
                         (select * from data."catalog" as c left join 
                        (SELECT distinct "variable"."id" as new_id, name_rus FROM meta.variable) as var on c.variable_id  = var.new_id) as foo 
                         on value.catalog_id =foo.id) as foo1
                        