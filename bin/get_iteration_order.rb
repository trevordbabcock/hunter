#!/usr/bin/env ruby

grid_height = 8
grid_width = 8

coords_list = []

grid_height.times do |n|
    grid_width.times do |m|
        coords_list << [n,m]
    end
end

puts coords_list.inspect