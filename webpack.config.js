const { resolve } = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');

module.exports = {
  mode: 'development',
  devtool: 'source-map',
  entry: {
    technote: [
      './src/assets/styles/technote.scss',
      './src/assets/scripts/technote.js',
    ],
  },
  output: {
    filename: 'scripts/[name].js',
    path: resolve(__dirname, 'src/technote/theme/static'),
  },
  plugins: [new MiniCssExtractPlugin({ filename: 'styles/[name].css' })],
  optimization: { minimizer: [`...`, new CssMinimizerPlugin()] },
  module: {
    rules: [
      {
        test: /\.(scss|css)$/i,
        use: [
          MiniCssExtractPlugin.loader,
          { loader: 'css-loader', options: { sourceMap: true } },
          { loader: 'postcss-loader', options: { sourceMap: true } },
          { loader: 'sass-loader', options: { sourceMap: true } },
        ],
      },
    ],
  },
};
