#!/usr/bin/env ruby

WATER = " \033[34m~\033[00m"
LAND = " \033[32mG\033[00m"
MOUNTAIN = " \033[31m^\033[00m"
FOREST = " \033[33mF\033[00m"

MAX_LIKELIHOOD = 100

LAND_ADJ_COEF_BASE = 8
LAND_ADJ_COEF_ADD = 26
LAND_ADJ_COEF_DIAG_ADD = 18

MOUNTAIN_ADJ_COEF_BASE = 2
MOUNTAIN_ADJ_COEF_ADD = 21
MOUNTAIN_ADJ_COEF_DIAG_ADD = 18

FOREST_ADJ_COEF_BASE = 5
FOREST_ADJ_COEF_ADD = 40
FOREST_ADJ_COEF_DIAG_ADD = 12
FOREST_MTN_ADJ_COEF_ADD = 5
FOREST_WTR_ADJ_COEF_SUBTRACT = 10

def generate_map(height, width)
  map = []

  height.times do |n|
    map[n] = []
    width.times do
      map[n] << WATER
    end
  end
  map = generate_land(map)
  map = generate_mountains(map)
  map = generate_forests(map)

  return map
end

def generate_land(map)
  map.each_with_index do |row,y|
    row.each_with_index do |cell,x|
      likelihood = LAND_ADJ_COEF_BASE
      likelihood = likelihood + LAND_ADJ_COEF_ADD if get_north(map, x, y) == LAND
      likelihood = likelihood + LAND_ADJ_COEF_ADD if get_south(map, x, y) == LAND
      likelihood = likelihood + LAND_ADJ_COEF_ADD if get_west(map, x, y) == LAND
      likelihood = likelihood + LAND_ADJ_COEF_ADD if get_east(map, x, y) == LAND
      likelihood = likelihood + LAND_ADJ_COEF_DIAG_ADD if get_northeast(map, x, y) == LAND
      likelihood = likelihood + LAND_ADJ_COEF_DIAG_ADD if get_southeast(map, x, y) == LAND
      likelihood = likelihood + LAND_ADJ_COEF_DIAG_ADD if get_southwest(map, x, y) == LAND
      likelihood = likelihood + LAND_ADJ_COEF_DIAG_ADD if get_northwest(map, x, y) == LAND

      if rand(MAX_LIKELIHOOD) < likelihood
        map[x][y] = LAND
      end
    end
  end
end

def generate_mountains(map)
  map.each_with_index do |row,y|
    row.each_with_index do |cell,x|
      if map[x][y] != WATER
        likelihood = MOUNTAIN_ADJ_COEF_BASE
        likelihood = likelihood + MOUNTAIN_ADJ_COEF_ADD if get_north(map, x, y) == MOUNTAIN
        likelihood = likelihood + MOUNTAIN_ADJ_COEF_ADD if get_south(map, x, y) == MOUNTAIN
        likelihood = likelihood + MOUNTAIN_ADJ_COEF_ADD if get_east(map, x, y) == MOUNTAIN
        likelihood = likelihood + MOUNTAIN_ADJ_COEF_ADD if get_west(map, x, y) == MOUNTAIN
        likelihood = likelihood + MOUNTAIN_ADJ_COEF_DIAG_ADD if get_northeast(map, x, y) == MOUNTAIN
        likelihood = likelihood + MOUNTAIN_ADJ_COEF_DIAG_ADD if get_southeast(map, x, y) == MOUNTAIN
        likelihood = likelihood + MOUNTAIN_ADJ_COEF_DIAG_ADD if get_southwest(map, x, y) == MOUNTAIN
        likelihood = likelihood + MOUNTAIN_ADJ_COEF_DIAG_ADD if get_northwest(map, x, y) == MOUNTAIN

        if rand(MAX_LIKELIHOOD) < likelihood
          map[x][y] = MOUNTAIN
        end
      end
    end
  end
end

def generate_forests(map)
  map.each_with_index do |row,y|
    row.each_with_index do |cell,x|
      if ![WATER, MOUNTAIN].include?(map[x][y])
        likelihood = FOREST_ADJ_COEF_BASE
        likelihood = likelihood + FOREST_ADJ_COEF_ADD if get_north(map, x, y) == FOREST
        likelihood = likelihood + FOREST_ADJ_COEF_ADD if get_south(map, x, y) == FOREST
        likelihood = likelihood + FOREST_ADJ_COEF_ADD if get_east(map, x, y) == FOREST
        likelihood = likelihood + FOREST_ADJ_COEF_ADD if get_west(map, x, y) == FOREST
        likelihood = likelihood + FOREST_ADJ_COEF_DIAG_ADD if get_northeast(map, x, y) == FOREST
        likelihood = likelihood + FOREST_ADJ_COEF_DIAG_ADD if get_southeast(map, x, y) == FOREST
        likelihood = likelihood + FOREST_ADJ_COEF_DIAG_ADD if get_southwest(map, x, y) == FOREST
        likelihood = likelihood + FOREST_ADJ_COEF_DIAG_ADD if get_northwest(map, x, y) == FOREST
        likelihood = likelihood + FOREST_MTN_ADJ_COEF_ADD if get_north(map, x, y) == MOUNTAIN
        likelihood = likelihood + FOREST_MTN_ADJ_COEF_ADD if get_south(map, x, y) == MOUNTAIN
        likelihood = likelihood + FOREST_MTN_ADJ_COEF_ADD if get_east(map, x, y) == MOUNTAIN
        likelihood = likelihood + FOREST_MTN_ADJ_COEF_ADD if get_west(map, x, y) == MOUNTAIN

        likelihood = likelihood - FOREST_WTR_ADJ_COEF_SUBTRACT if get_north(map, x, y) == WATER
        likelihood = likelihood - FOREST_WTR_ADJ_COEF_SUBTRACT if get_south(map, x, y) == WATER
        likelihood = likelihood - FOREST_WTR_ADJ_COEF_SUBTRACT if get_east(map, x, y) == WATER
        likelihood = likelihood - FOREST_WTR_ADJ_COEF_SUBTRACT if get_west(map, x, y) == WATER

        if rand(MAX_LIKELIHOOD) < likelihood
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


seed = ARGV[0] || rand(1000000000)
srand(seed.to_i)
map = generate_map(64, 64)
print_map(map)
puts "Seed: #{seed}"
