select date_loc, value,  site.name as site_name, site.code as site_code,  lon, lat,  new_id as value_id, name_rus from (select date_loc, value, catalog_id, site_id, new_id, name_rus from data.data_value as value left join 
                         (select * from data."catalog" as c left join 
                        (SELECT distinct "variable"."id" as new_id, name_rus FROM meta.variable) as var on c.variable_id  = var.new_id) as foo 
                         on value.catalog_id =foo.id 
                        where new_id = 1021) as foo2 left join meta.site as site on foo2.site_id = site.id
                        