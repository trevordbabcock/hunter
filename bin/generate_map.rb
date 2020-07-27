#!/usr/bin/env ruby

require 'json'

WATER = " \033[34m~\033[00m"
LAND = " \033[32mG\033[00m"
MOUNTAIN = " \033[31m^\033[00m"
FOREST = " \033[33mF\033[00m"


class Map
  attr_accessor :grid

  def initialize(height, width)
    @grid = []
    @height = height
    @width = width

    @height.times do |n|
      row = []
      @width.times do |m|
        row << Cell.new(m, n, WATER)
      end
      @grid[n] = row
    end
  end

  def render()
    @grid.reverse.each do |r|
      r.each do |c|
        print c.value
      end

      puts
    end
  end

  def cell(x, y)
    if(@grid[y])
      return @grid[y][x]
    else
      return nil
    end
  end
  
  def north_of(x, y)
    cell(x, y+1)
  end
  
  def northeast_of(x, y)
    cell(x+1, y+1)
  end
  
  def east_of(x, y)
    cell(x+1, y)
  end
  
  def southeast_of(x, y)
    cell(x+1, y-1)
  end
  
  def south_of(x, y)
    cell(x, y-1)
  end
  
  def southwest_of(x, y)
    cell(x-1, y-1)
  end
  
  def west_of(x, y)
    cell(x-1, y)
  end
  
  def northwest_of(x, y)
    cell(x-1, y+1)
  end
end

class Cell
  attr_accessor :x, :y, :value

  def initialize(x, y, value)
    @x = x
    @y = y
    @value = value
  end
end

def generate_map(height, width, config, iteration_order)
  map = Map.new(height, width)

  map.grid.each do |r|
    r.each do |c|
      c = WATER
    end
  end

  map = generate_land(map, config["land"], iteration_order)
  map = generate_mountains(map, config["mountain"], iteration_order)
  map = generate_forests(map, config["forest"], iteration_order)

  return map
end

def generate_land(map, config, iteration_order)
  iteration_order.each do |coord|
    x, y = coord

    likelihood = config["base-percentage"]
    likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if map.north_of(x, y) && map.north_of(x, y).value == LAND
    likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if map.south_of(x, y) && map.south_of(x, y).value == LAND
    likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if map.west_of(x, y) && map.west_of(x, y).value == LAND
    likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if map.east_of(x, y) && map.east_of(x, y).value == LAND
    likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if map.northeast_of(x, y) && map.northeast_of(x, y).value == LAND
    likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if map.southeast_of(x, y) && map.southeast_of(x, y).value == LAND
    likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if map.southwest_of(x, y) && map.southwest_of(x, y).value == LAND
    likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if map.northwest_of(x, y) && map.northwest_of(x, y).value == LAND

    if rand(config["max-likelihood"]) < likelihood
      map.cell(x, y).value = LAND
    end
  end

  return map
end

def generate_mountains(map, config, iteration_order)
  iteration_order.each do |coord|
    x, y = coord

    if map.cell(x, y).value != WATER
      likelihood = config["base-percentage"]
      likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if map.north_of(x, y) && map.north_of(x, y).value == MOUNTAIN
      likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if map.south_of(x, y) && map.south_of(x, y).value == MOUNTAIN
      likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if map.east_of(x, y) && map.east_of(x, y).value == MOUNTAIN
      likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if map.west_of(x, y) && map.west_of(x, y).value == MOUNTAIN
      likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if map.northeast_of(x, y) && map.northeast_of(x, y).value == MOUNTAIN
      likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if map.southeast_of(x, y) && map.southeast_of(x, y).value == MOUNTAIN
      likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if map.southwest_of(x, y) && map.southwest_of(x, y).value == MOUNTAIN
      likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if map.northwest_of(x, y) && map.northwest_of(x, y).value == MOUNTAIN

      if rand(config["max-likelihood"]) < likelihood
        map.cell(x, y).value = MOUNTAIN
      end
    end
  end

  return map
end

def generate_forests(map, config, iteration_order)
  iteration_order.each do |coord|
    x, y = coord
    if ![WATER, MOUNTAIN].include?(map.cell(x, y))
      likelihood = config["base-percentage"]
      likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if map.north_of(x, y) && map.north_of(x, y).value == FOREST
      likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if map.south_of(x, y) && map.south_of(x, y).value == FOREST
      likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if map.east_of(x, y) && map.east_of(x, y).value == FOREST
      likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if map.west_of(x, y) && map.west_of(x, y).value == FOREST
      likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if map.northeast_of(x, y) && map.northeast_of(x, y).value == FOREST
      likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if map.southeast_of(x, y) && map.southeast_of(x, y).value == FOREST
      likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if map.southwest_of(x, y) && map.southwest_of(x, y).value == FOREST
      likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if map.northwest_of(x, y) && map.northwest_of(x, y).value == FOREST

      likelihood = likelihood + config["mountain-adjacency-add-percentage"] if map.north_of(x, y) && map.north_of(x, y).value == MOUNTAIN
      likelihood = likelihood + config["mountain-adjacency-add-percentage"] if map.south_of(x, y) && map.south_of(x, y).value == MOUNTAIN
      likelihood = likelihood + config["mountain-adjacency-add-percentage"] if map.east_of(x, y) && map.east_of(x, y).value == MOUNTAIN
      likelihood = likelihood + config["mountain-adjacency-add-percentage"] if map.west_of(x, y) && map.west_of(x, y).value == MOUNTAIN

      likelihood = likelihood - config["water-adjacency-subtract-percentage"] if map.north_of(x, y) && map.north_of(x, y).value == WATER
      likelihood = likelihood - config["water-adjacency-subtract-percentage"] if map.south_of(x, y) && map.south_of(x, y).value == WATER
      likelihood = likelihood - config["water-adjacency-subtract-percentage"] if map.east_of(x, y) && map.east_of(x, y).value == WATER
      likelihood = likelihood - config["water-adjacency-subtract-percentage"] if map.west_of(x, y) && map.west_of(x, y).value == WATER

      if rand(config["max-likelihood"]) < likelihood
        map.cell(x, y).value = FOREST
      end
    end
  end

  return map
end

def get_iteration_order(type, grid_height, grid_width)
  coords_list = []

  grid_height.times do |n|
    grid_width.times do |m|
      coords_list << [m,n]
    end
  end

  if type == "standard"
    # do nothing
  elsif type == "shuffle"
    coords_list.shuffle!
  end

  return coords_list
end


if ARGV.count == 0
  puts "generate_map.rb [dimensions] [config_file_path] [seed]"
  puts "Example: generate_map.rb 64x64 config/standard-map.json 1235"
else
  map_height, map_width = ARGV[0].split("x").collect{|d| d.to_i}

  config_file_path = ARGV[1]
  file_contents = File.read(config_file_path)
  config = JSON.parse(file_contents)

  seed = ARGV[2] || rand(1000000000)
  srand(seed.to_i)

  map = generate_map(map_height, map_width, config, get_iteration_order(config["iteration_type"], map_height, map_width))
  map.render()
  
  puts "Config: #{config_file_path}"
  puts "Dimensions: #{map_height}x#{map_width}"
  puts "Seed: #{seed}"
end
