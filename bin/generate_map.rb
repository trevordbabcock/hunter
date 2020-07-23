#!/usr/bin/env ruby

require 'json'


WATER = " \033[34m~\033[00m"
LAND = " \033[32mG\033[00m"
MOUNTAIN = " \033[31m^\033[00m"
FOREST = " \033[33mF\033[00m"

MAX_LIKELIHOOD = 100

# LAND_ADJ_COEF_BASE = 8
# LAND_ADJ_COEF_ADD = 26
# LAND_ADJ_COEF_DIAG_ADD = 18

# MOUNTAIN_ADJ_COEF_BASE = 2
# MOUNTAIN_ADJ_COEF_ADD = 21
# MOUNTAIN_ADJ_COEF_DIAG_ADD = 18

# FOREST_ADJ_COEF_BASE = 5
# FOREST_ADJ_COEF_ADD = 40
# FOREST_ADJ_COEF_DIAG_ADD = 12
# FOREST_MTN_ADJ_COEF_ADD = 5
# FOREST_WTR_ADJ_COEF_SUBTRACT = 10


def generate_map(height, width, config)
  map = []

  height.times do |n|
    map[n] = []
    width.times do
      map[n] << WATER
    end
  end
  map = generate_land(map, config["land"])
  map = generate_mountains(map, config["mountain"])
  map = generate_forests(map, config["forest"])

  return map
end

def generate_land(map, config)
  map.each_with_index do |row,y|
    row.each_with_index do |cell,x|
      likelihood = config["base-percentage"]
      likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if get_north(map, x, y) == LAND
      likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if get_south(map, x, y) == LAND
      likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if get_west(map, x, y) == LAND
      likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if get_east(map, x, y) == LAND
      likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if get_northeast(map, x, y) == LAND
      likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if get_southeast(map, x, y) == LAND
      likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if get_southwest(map, x, y) == LAND
      likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if get_northwest(map, x, y) == LAND

      if rand(config["max-likelihood"]) < likelihood
        map[x][y] = LAND
      end
    end
  end
end

def generate_mountains(map, config)
  map.each_with_index do |row,y|
    row.each_with_index do |cell,x|
      if map[x][y] != WATER
        likelihood = config["base-percentage"]
        likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if get_north(map, x, y) == MOUNTAIN
        likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if get_south(map, x, y) == MOUNTAIN
        likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if get_east(map, x, y) == MOUNTAIN
        likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if get_west(map, x, y) == MOUNTAIN
        likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if get_northeast(map, x, y) == MOUNTAIN
        likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if get_southeast(map, x, y) == MOUNTAIN
        likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if get_southwest(map, x, y) == MOUNTAIN
        likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if get_northwest(map, x, y) == MOUNTAIN

        if rand(config["max-likelihood"]) < likelihood
          map[x][y] = MOUNTAIN
        end
      end
    end
  end
end

def generate_forests(map, config)
  map.each_with_index do |row,y|
    row.each_with_index do |cell,x|
      if ![WATER, MOUNTAIN].include?(map[x][y])
        likelihood = config["base-percentage"]
        likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if get_north(map, x, y) == FOREST
        likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if get_south(map, x, y) == FOREST
        likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if get_east(map, x, y) == FOREST
        likelihood = likelihood + config["orthogonal-adjacency-add-percentage"] if get_west(map, x, y) == FOREST
        likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if get_northeast(map, x, y) == FOREST
        likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if get_southeast(map, x, y) == FOREST
        likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if get_southwest(map, x, y) == FOREST
        likelihood = likelihood + config["diagonal-adjacency-add-percentage"] if get_northwest(map, x, y) == FOREST

        likelihood = likelihood + config["mountain-adjacency-add-percentage"] if get_north(map, x, y) == MOUNTAIN
        likelihood = likelihood + config["mountain-adjacency-add-percentage"] if get_south(map, x, y) == MOUNTAIN
        likelihood = likelihood + config["mountain-adjacency-add-percentage"] if get_east(map, x, y) == MOUNTAIN
        likelihood = likelihood + config["mountain-adjacency-add-percentage"] if get_west(map, x, y) == MOUNTAIN

        likelihood = likelihood - config["water-adjacency-subtract-percentage"] if get_north(map, x, y) == WATER
        likelihood = likelihood - config["water-adjacency-subtract-percentage"] if get_south(map, x, y) == WATER
        likelihood = likelihood - config["water-adjacency-subtract-percentage"] if get_east(map, x, y) == WATER
        likelihood = likelihood - config["water-adjacency-subtract-percentage"] if get_west(map, x, y) == WATER

        if rand(config["max-likelihood"]) < likelihood
          map[x][y] = FOREST
        end
      end
    end
  end
end

def get_cell_or_nil(map, x, y)
  if(map[x])
    return map[x][y]
  end
  return nil
end

def get_north(map, x, y)
  get_cell_or_nil(map, x, y+1)
end

def get_northeast(map, x, y)
  get_cell_or_nil(map, x+1, y+1)
end

def get_east(map, x, y)
  get_cell_or_nil(map, x+1, y)
end

def get_southeast(map, x, y)
  get_cell_or_nil(map, x+1, y-1)
end

def get_south(map, x, y)
  get_cell_or_nil(map, x, y-1)
end

def get_southwest(map, x, y)
  get_cell_or_nil(map, x-1, y-1)
end

def get_west(map, x, y)
  get_cell_or_nil(map, x-1, y)
end

def get_northwest(map, x, y)
  get_cell_or_nil(map, x-1, y+1)
end

def print_map(map)
  map.each do |row|
    row.each do |cell|
      print cell
    end
    puts
  end
end

if ARGV.count == 0
  puts "generate_map.rb [dimensions] [config_file_path] [seed]"
  puts "Example: generate_map.rb 64x64 config/standard-map.json 1235"
else
  map_height, map_width = ARGV[0].split("x")

  config_file_path = ARGV[1]
  file_contents = File.read(config_file_path)
  config = JSON.parse(file_contents)

  seed = ARGV[2] || rand(1000000000)
  srand(seed.to_i)

  map = generate_map(map_height.to_i, map_width.to_i, config)
  print_map(map)
  puts "Config: #{config_file_path}"
  puts "Dimensions: #{map_height}x#{map_width}"
  puts "Seed: #{seed}"
end
