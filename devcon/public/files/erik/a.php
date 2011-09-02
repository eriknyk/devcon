#!/usr/bin/env php
<?php
list($a, $b) = explode(' ', trim(fgets(STDIN)));

while($a != 0) {
  echo ($a + $b) . "\n";
  @list($a, $b) = explode(' ', trim(fgets(STDIN)));
}

