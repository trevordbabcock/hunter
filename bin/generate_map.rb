#!/usr/bin/env ruby

WATER = " ~"
LAND = " G"

LAND_ADJ_COEF_BASE = 10
LAND_ADJ_COEF_ADD = 26
LAND_ADJ_COEF_DIAG_ADD = 18

def generate_map(height, width)
  map = []

  height.times do |n|
    map[n] = []
    width.times do
      map[n] << WATER
    end
  end
  map = generate_land(map)

  return map
end

def generate_land(map)
  map.each_with_index do |row,y|
    row.each_with_index do |cell,x|
      likelihood = LAND_ADJ_COEF_BASE
      likelihood = likelihood + LAND_ADJ_COEF_ADD if get_cell_or_nil(map, x+1, y) == LAND # up
      likelihood = likelihood + LAND_ADJ_COEF_ADD if get_cell_or_nil(map, x-1, y) == LAND # down
      likelihood = likelihood + LAND_ADJ_COEF_ADD if get_cell_or_nil(map, x, y-1) == LAND # left
      likelihood = likelihood + LAND_ADJ_COEF_ADD if get_cell_or_nil(map, x, y+1) == LAND # right
      likelihood = likelihood + LAND_ADJ_COEF_DIAG_ADD if get_cell_or_nil(map, x-1, y-1) == LAND # upleft
      likelihood = likelihood + LAND_ADJ_COEF_DIAG_ADD if get_cell_or_nil(map, x-1, y+1) == LAND # downleft
      likelihood = likelihood + LAND_ADJ_COEF_DIAG_ADD if get_cell_or_nil(map, x+1, y-1) == LAND # upright
      likelihood = likelihood + LAND_ADJ_COEF_DIAG_ADD if get_cell_or_nil(map, x+1, y+1) == LAND # downright

      if rand(100) < likelihood
        map[x][y] = LAND
      end
    end
  end
end

def get_cell_or_nil(map, x, y)
  tmp = map[x]
  if(map[x])
    tmp2 = map[x][y]
    return map[x][y]
  end
  return nil
end

def print_map(map)
  map.each do |row|
    row.each do |cell|
      print cell
    end
    puts
  end
end

map = generate_map(64, 64)
print_map(map)
